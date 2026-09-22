# Session 03 — Action으로 AMR 이동·취소·실패·중복 처리

> 난이도: 중급 / 예상 4~6시간 / GPU: 불필요
> 선행: Session 02

## 1. 왜 Action인가

AMR 이동에는 “명령을 받았다”와 “목적지에 도착했다” 사이에 시간이 있습니다.
또한 진행 피드백과 취소가 필요합니다. 이 과정에서는 Action으로 해당 계약을 구성합니다.[R1, R2]

**구분해야 할 사건**
1. 발견: 서버 endpoint를 찾음.
2. 접수: Goal 수락/거부.
3. 진행: Feedback.
4. 종료: Result와 terminal status.
5. 취소: 요청·수락·실제 종료의 단계.

수락 응답을 작업 완료로 변환하는 Adapter는 이 테스트에서 실패해야 합니다.

## 2. 학습 Action 정의

`MoveTo.action`:

```text
string task_id
float64 x
float64 y
float64 speed
float64 timeout_sec
---
bool success
string code
string detail
---
float64 remaining_m
string phase
```

앞부분은 Goal, 가운데는 Result, 마지막은 Feedback입니다.
목표 yaw·지도 선택·경로 예약은 아직 포함하지 않았습니다.
전체 계약: [INTERFACE_CONTRACT](../appendices/INTERFACE_CONTRACT.md).

## 3. 코드 구조: 상태 머신과 ROS를 분리

- `core.py`: 좌표·입력 검증·중복·상태 전이·타임아웃.
- `amr_server.py`: GoalHandle·메시지·타이머·cmd_vel.
- `move_client.py`: 요청·결과·취소·제한된 대기.

예제의 순수 로직:

```python
m.start(Request("task-A", x=1.0, y=0.0, speed=0.3))
m.tick(0.05)
m.cancel()
assert m.phase == "CANCELED"
```

이 코드는 ROS가 없어도 테스트됩니다.
`Motion`에는 Isaac import가 없어 backend 변경이 상태 머신 전체를 다시 쓰는 작업이 되지 않도록 합니다.

## 4. 동시 요청과 예약

서버의 `goal_callback`에서 유효성 검사와 `Motion.start()`를 수행합니다.
여기서 busy 상태를 예약하므로, accepted 콜백 전에 다른 요청이 들어와도 이중 수락을 막는 설계입니다.

```python
try:
    self.motion.start(Request(msg.task_id, msg.x, msg.y,
                              msg.speed, msg.timeout_sec))
except ValueError:
    return GoalResponse.REJECT
return GoalResponse.ACCEPT
```

`accepted` 콜백은 해당 GoalHandle에 Future를 만들고 실행을 시작합니다.
`execute`는 CPU를 붙잡는 while/sleep 대신 Future를 기다립니다.

```python
async def execute(self, handle):
    key = self.key(handle)
    try:
        return await self.futures[key]
    finally:
        self.futures.pop(key, None)
```

실제 진행은 짧은 timer 콜백이 담당합니다.
이 구조에서 cancel 처리가 별도 이벤트로 들어올 수 있도록 ReentrantCallbackGroup을 사용합니다.
코드의 동시성 가정은 Session 04에서 다룹니다.

## 5. 실습 A — 성공과 피드백

서버 실행 후:

```bash
ros2 action send_goal /amr_01/move_to study_interfaces/action/MoveTo \
  "{task_id: s03-A, x: 1.0, y: 0.0, speed: 0.3, timeout_sec: 30.0}" \
  --feedback
```

확인할 것:
- Goal 수락 시각.
- remaining_m 감소.
- terminal status SUCCEEDED.
- Result의 success와 code.

이 예제는 같은 좌표에 이미 도착한 경우에도 다음 tick에 완료 판정을 수행합니다.

## 6. 실습 B — 취소

```bash
ros2 run study_nodes move_client --ros-args \
  -r __ns:=/amr_01 -p x:=5.0 -p cancel_after_sec:=0.5
```

예상 조건: 취소가 작업 종료 전에 처리되면 `CANCEL_REQUESTED` 결과.
취소를 너무 늦게 보내면 이미 완료됐을 수 있으므로 SUCCESS를 무조건 오류로 보지 않습니다.
**합격 기준은 명세된 경쟁 처리 정책과 최종 상태가 일치하는가입니다.**

예제는 취소 요청을 관측하면 0속도 발행 후 CANCELED로 종료합니다.
실제 로봇 정지 확인까지 기다리는 구현이 아니므로 물리 취소 검증에는 추가 단계가 필요합니다.

## 7. 실습 C — 거부·중복·장애·타임아웃

| 입력 | 기대 동작 |
|---|---|
| speed=0 | Goal 거부 |
| 같은 task_id 재전송 | 프로세스 내 ledger에 있으면 거부 |
| 작업 중 두 번째 Goal | BUSY 거부 |
| 작업 중 reset_idle | Service 실패 |
| 작업 중 set_fault=true | FAILED / INJECTED_FAULT |
| 거리 대비 짧은 timeout | FAILED / TIMEOUT |

timeout 예시:

```bash
ros2 action send_goal /amr_01/move_to study_interfaces/action/MoveTo \
  "{task_id: s03-timeout, x: 50.0, y: 0.0, speed: 0.1, timeout_sec: 0.5}"
```

서버 장애 플래그를 해제하고 다음 실습을 진행합니다.
task_id가 중복되어 의도와 다르게 거부되면 새 ID를 사용하되, 중복 실험에서는 일부러 같은 ID를 유지합니다.

## 8. 멱등성의 정확한 범위

제공 코드는 **중복 거부**를 구현하지, 동일 요청에 이전 결과를 돌려주는 완전한 멱등 API를 구현하지 않습니다.
- 메모리 ledger 최대 1024개.
- 가득 차면 신규 요청 거부.
- soft reset으로 지우지 않음.
- 프로세스 재시작 시 소실.

운영 확장:
1. `(device_id, task_id)`를 저장.
2. 요청 payload hash도 보관.
3. 같은 ID·같은 payload면 기존 실행/결과 조회.
4. 같은 ID·다른 payload면 계약 오류.
5. 영구 저장 성공과 장비 실행 사이의 장애 창을 다룸.

ROS goal UUID와 업무 task_id는 별도로 기록합니다.

## 9. 주의사항과 고급 과제

- ActionClient 호출 Future 완료는 최종 결과가 아닐 수 있습니다. 접수와 결과 Future를 구분합니다.
- 클라이언트 종료가 자동 정지 보장은 아닙니다.
- 예제 client는 결과를 못 받으면 UNKNOWN으로 해석하도록 오류를 냅니다.
- 취소 응답을 받았어도 결과/물리 정지는 추가 확인해야 합니다.
- 도착 판정은 XY 거리만 확인합니다. 실제 인계에는 yaw·속도·도킹 점유가 필요합니다.
- 장애물 회피가 없으므로 임의의 실제 robot cmd_vel endpoint에 연결하지 마십시오.

**고급 과제:** 영구 이력 조회 Service, 진행 중 상태 복구, 도착 유지시간 조건을 설계합니다.

## 10. 완료 기준

- [ ] 접수/피드백/결과를 로그에서 구분한다.
- [ ] 정상·취소·실패·중복·BUSY를 각각 재현했다.
- [ ] 같은 tick에서 취소와 도착이 겹치는 정책을 설명한다.
- [ ] 예제의 중복 방지 범위를 재시작까지 확장해서 과장하지 않는다.

## 11. 질문과 해설

**Q. Goal이 거부됐는데 Result의 code를 왜 못 받나요?**  
수락되지 않은 Goal의 업무 결과를 기다리는 계약이 아니기 때문입니다. 상세 거부 조회는 별도 설계가 필요합니다.

**Q. `success=false`만 있으면 충분한가요?**  
취소·장애·통신 UNKNOWN의 원인과 복구 정책이 달라 코드와 terminal status도 해석해야 합니다.

**Q. Reliable로 바꾸면 중복 실행이 사라지나요?**  
아니요. 전송 정책과 업무 멱등성은 다른 계층입니다.

## 다음 단계
[Session 04](04_qos_concurrency_time.md).

## 참고
[R1, R2, R3, R6] 범위와 코드 검증 등급: [SOURCES](../appendices/SOURCES.md), [VALIDATION](../appendices/VALIDATION.md).
