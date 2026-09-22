# Session 02 — Topic·Service·장비 상태와 재시작 감지

> 난이도: 입문~중급 / 예상 3~4시간 / GPU: 불필요
> 선행: Session 01 빌드 완료

## 1. 이번에 구현·관찰할 것

- Topic으로 지속적인 장비 상태 수신.
- 짧은 Service로 상태 초기화 요청.
- 서버 재시작과 단순 통신 지연의 구분.
- “응답이 없다”를 “IDLE이다”로 변환하지 않는 원칙.

Topic은 지속 데이터, Service는 짧은 요청·응답을 학습하는 데 사용합니다.[R1]
장시간 이동을 Service 응답이 올 때까지 묶어두는 대신 다음 세션의 Action으로 처리합니다.

## 2. DeviceState 계약 읽기

실제 파일: `examples/ros2_ws/src/study_interfaces/msg/DeviceState.msg`

```text
builtin_interfaces/Time stamp
string device_id
string boot_id
uint64 sequence
string task_id
string phase
float64 x
float64 y
string detail
```

프로젝트 의미:
- `device_id`: 장비의 안정적인 식별자.
- `boot_id`: 서버 프로세스 시작마다 새 UUID. 재시작 경계.
- `sequence`: 해당 프로세스에서 상태 발행 순서.
- `task_id`: 현재 또는 마지막 작업의 업무 ID.
- `phase`: 교재 상태 머신의 상태.
- `stamp`: ROS 시각. heartbeat 경과시간 판정에는 별도 수신 monotonic 시간을 사용.

**실제 통신 계약에서는** 오류 코드·프레임·버전·run_id 등을 추가할 수 있습니다.
여기서는 문자열 JSON 하나에 모든 내용을 넣지 않고 최소한의 타입을 정의합니다.

## 3. 코드 해설 — 상태 발행

`amr_server.py`에서 다음 흐름을 확인하십시오.

```python
msg.stamp = self.get_clock().now().to_msg()
msg.device_id, msg.boot_id = self.device_id, self.boot_id
self.sequence += 1
msg.sequence = self.sequence
msg.phase = self.motion.phase
self.state_pub.publish(msg)
```

이 코드의 값은 예제 상태 모델에서 가져옵니다.
mock 상태를 “실제 센서가 측정한 상태”라고 표시해서는 안 됩니다.
로그에는 backend 종류도 함께 남기는 확장을 권장합니다.

## 4. 실습 A — 상태를 세 가지 방법으로 관찰

서버가 `/amr_01`에서 실행 중인 상태:

```bash
ros2 topic echo /amr_01/state
ros2 topic hz /amr_01/state
ros2 topic info /amr_01/state --verbose
```

명령별 새 터미널을 쓰거나 순차 종료하여 실행합니다.

기대 조건:
- phase는 초기 `IDLE`.
- sequence가 증가.
- 설정상 0.2초마다 발행하므로 약 5Hz가 의도된 값.
- 관측 주기는 OS 부하·통신·CLI 관찰 비용에 따라 다를 수 있음.

**기록 과제:** publisher 설정 주기와 CLI 관측 주기가 다른 이유를 2가지 적습니다.

## 5. 실습 B — 짧은 상태 초기화 Service

```bash
ros2 service call /amr_01/reset_idle std_srvs/srv/Trigger "{}"
```

기대: 작업 비활성 상태라면 success=true.
이 서비스는 물리 씬을 초기화하거나 위치를 원점으로 되돌리지 않습니다.
이미 끝난 작업 상태를 IDLE로 바꾸고, 위치와 중복 ledger는 보존합니다.

`reset_idle()`의 핵심:

```python
if self.busy:
    raise ValueError("BUSY")
self.phase, self.detail = "IDLE", ""
self.request = None
```

작업 실행 중의 reset은 다음 세션에서 거부되는지 확인합니다.
리셋의 범위를 명세하지 않으면 Adapter가 “위치까지 초기화됐다”고 오해할 수 있습니다.

## 6. 실습 C — 재시작과 통신 중단

다른 터미널:

```bash
ros2 run study_nodes state_watch --ros-args -r __ns:=/amr_01
```

1. 상태를 수신합니다.
2. AMR 서버만 종료합니다.
3. 감시 노드에서 약 1초 이상 경과 뒤 UNKNOWN 경고를 관찰합니다.
4. 서버를 다시 실행합니다.
5. boot_id 변경 경고를 관찰합니다.

감시 노드는 한번도 상태를 받지 못한 경우에는 stale 경고를 내지 않는 간단한 예제입니다.
**확장 과제:** 시작 이후 일정 시간동안 최초 상태가 없을 때 `NOT_READY`를 보고하도록 수정하십시오.

## 7. 상태와 이벤트를 구분하기

설계 제안:
- 상태: “현재 무엇인가”를 주기적으로 알림.
- 이벤트: “언제 무엇이 바뀌었는가”를 별도 보관.
- 작업 이력: “그 요청이 과거에 어떻게 끝났는가”를 조회.

주기 상태만으로 모든 이벤트를 복구할 수 있다고 가정하지 않습니다.
예를 들어 IDLE→RUNNING→FAILED→IDLE이 상태 발행 사이에 지나가면 중간 전이를 놓칠 수 있습니다.
예제에는 영구 이벤트 저장소가 없습니다. 운영 단계에서 별도로 추가합니다.

## 8. 주의사항·고급 기술

- reliable 수신을 쓴다고 애플리케이션의 작업 결과 이력이 영구 보존되는 것은 아닙니다.
- snapshot 상태의 늦은 구독자 정책과 명령 재실행 정책은 분리합니다.
- 콜백에서 Service 완료를 동기 대기하지 않는 방향을 우선합니다.[R5]
- Service의 타임아웃은 “요청이 적용되지 않았다”는 증거가 아닙니다.
- 조회·설정·재실행의 멱등성 규칙을 구분하십시오.
- reset은 의미가 명확할 때만 허용합니다. 중간 화물 소유권을 임의 삭제하지 않습니다.

## 9. 운영 고려사항

- heartbeat 수신 시간을 host 단위로 측정하고 타 서버의 monotonic 값과 직접 차감하지 않습니다.
- 장비 연결 여부와 작업 상태를 독립 필드로 다루는 확장을 검토합니다.
- 로그에 boot_id를 넣어 재시작 전후 동일 task_id를 구분합니다.
- 경고 반복 출력은 제한하되 복구 이벤트는 반드시 남깁니다.
- 장애 후 상태가 돌아왔다고 작업을 자동 재전송하지 않습니다.

## 10. 완료 기준

- [ ] 상태를 타입·주기·QoS 관점으로 확인했다.
- [ ] reset의 성공과 거부 범위를 설명한다.
- [ ] 서버 재시작을 boot_id로 구분했다.
- [ ] 무응답을 UNKNOWN으로 취급한다.

## 11. 질문과 해설

**Q. timestamp만 있으면 sequence는 불필요한가요?**  
이 설계에서는 시계 되감김·동일 시각·발행 순서를 구분하려고 sequence도 둡니다. 서로 다른 목적입니다.

**Q. IDLE로 초기화하면 동일 작업을 다시 실행해도 되나요?**  
제공 모델은 ledger를 보존하므로 같은 task_id를 거부합니다. reset과 중복 정책은 별도입니다.

**Q. Service 응답이 유실되면 다시 호출해도 되나요?**  
연산의 멱등성과 조회 가능성에 따라 다릅니다. 무조건 재시도하지 않습니다.

## 다음 단계
[Session 03](03_actions_and_mock_amr.md).

## 참고
[R1, R5], [인터페이스 계약](../appendices/INTERFACE_CONTRACT.md),
[SOURCES](../appendices/SOURCES.md).
