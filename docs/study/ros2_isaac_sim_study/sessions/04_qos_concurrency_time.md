# Session 04 — QoS·콜백·실행기·시뮬레이션 시간

> 난이도: 중급 / 예상 3~5시간 / GPU: 기본 과제 불필요
> 선행: Session 03

## 1. 이 세션의 질문

- Topic이 보이는데 왜 데이터가 안 올까요?
- Action이 실행되는 동안 취소가 왜 늦어질까요?
- 시뮬레이터를 일시정지하면 통신 타임아웃도 멈춰야 할까요?

이 세 문제를 각각 **QoS**, **실행기/콜백 구조**, **시계 정책**으로 분리합니다.

## 2. QoS를 계약으로 취급하기

QoS에는 reliability, durability, history/depth 등의 설정이 있으며 호환되는 endpoint끼리 연결됩니다.[R4]
본 교재의 설정은 다음과 같습니다.

| 데이터 | 예제 정책 | 이유/한계 |
|---|---|---|
| DeviceState | Reliable + Volatile, depth 10 | 주기 상태; 영구 이벤트 저장소는 아님 |
| cmd_vel | Reliable + Volatile, depth 10 | 학습용. 오래된 속도 명령 적체 위험은 별도 검증 |
| odom 수신 | BestEffort, depth 5 | 센서 계열 송신과 연결 실습 |
| 업무 Action | 명시하지 않은 endpoint는 ROS 기본 설정 | 실제 배포 전 endpoint별 확인 |

설정 코드:

```python
qos = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
)
```

“항상 Reliable이 더 좋다”는 정책으로 통일하지 않습니다.
주기 상태, 이벤트, 영상, 제어 명령은 손실·지연·적체의 비용이 다릅니다.

## 3. 실습 A — 의도적으로 QoS 불일치 만들기

별도 실습 Topic을 사용합니다. 실제 명령 Topic에 실험하지 마십시오.

터미널 A:

```bash
ros2 topic pub /qos_lab std_msgs/msg/String "{data: hello}" \
  --rate 2 --qos-reliability best_effort
```

터미널 B:

```bash
ros2 topic echo /qos_lab std_msgs/msg/String \
  --qos-reliability reliable
```

그 다음 subscriber를 best_effort로 바꿔 비교합니다.
CLI 옵션이 설치판과 다르면 `ros2 topic pub --help`, `echo --help`로 먼저 확인합니다.

관찰 기록:
- graph에는 endpoint가 있는가?
- 실제 메시지가 수신되는가?
- incompatible QoS 경고가 있는가?
- 호환되도록 변경한 뒤 무엇이 달라졌는가?

## 4. Executor와 CallbackGroup을 함께 읽기

ROS 콜백 그룹은 동시 실행 허용 범위를 제어합니다.
상호배제 그룹은 그룹 내부 중첩 실행을 막고, 재진입 그룹은 중첩 가능성을 허용합니다.
MultiThreadedExecutor만 바꾸고 모든 콜백을 기본 상호배제 그룹에 두면 기대한 병렬성이 나오지 않을 수 있습니다.[R3]

**제공 코드의 의도**
- 장비당 SingleThreadedExecutor.
- Action에는 ReentrantCallbackGroup.
- execute는 Future 대기로 양보.
- timer·서비스·취소는 짧게 처리.
- 공유 상태는 RLock으로 보호하지만, 예제가 임의의 멀티스레드 변경까지 검증됐다는 의미는 아님.

같은 execute 콜백에서 긴 blocking loop를 돌리면 단일 실행기에서 다른 콜백이 지연될 수 있습니다.
별도 asyncio event loop를 구성하지 않은 상태에서 `asyncio.sleep()`을 ROS Future와 임의 혼합하지 않습니다.

## 5. 금지 패턴과 대안

주의용 예시 — 아래 코드를 실행 경로에 넣지 마십시오.

```python
def timer_callback():
    # 예: 같은 실행 경로에서 결과를 동기 대기
    response = client.call(request)
```

대안은 `call_async()`와 완료 콜백을 사용하거나, 비동기 상태 머신으로 다음 단계를 넘기는 것입니다.[R5]
무한 대기·잠금 순서·Future 완료 경로를 함께 검토하십시오.

**실습 B:** `amr_server.py`에서 active Goal이 결과로 끝나는 경로를 표시합니다.
- 성공
- 취소
- 주입 장애
- pose stale
- timeout

예외 발생 시 Future가 영원히 미완료로 남는 경로가 없는지 검토합니다.
예제는 운영용 최상위 예외 수습·저장소 복구까지 구현하지 않았습니다.

## 6. 세 가지 시간

| 시간 | 본 과정 용도 |
|---|---|
| ROS clock | state stamp, sim clock 연결 |
| host monotonic | 응답 latency, task timeout, watchdog |
| 실제 UTC/KST 시각 | 사람이 보는 로그 상관관계 |

코드:

```python
steady = Clock(clock_type=ClockType.STEADY_TIME)
timer = node.create_timer(0.2, callback, clock=steady)
start = time.monotonic()
```

`use_sim_time=true`여도 watchdog timer는 steady clock을 명시했습니다.
본 과정에서는 시뮬레이터 pause 중에도 통신·작업 timeout이 진행됩니다.
다른 정책을 원하면 “생산 작업 timeout은 sim time, 통신은 wall time”처럼 별도 계약으로 바꾸고 테스트합니다.

## 7. 실습 C — 시계 정지 실험

GPU 없이도 서버에 `use_sim_time=true`를 주고 `/clock`을 발행하지 않는 실험을 할 수 있습니다.

```bash
ros2 run study_nodes amr_server --ros-args \
  -r __ns:=/amr_clock_lab -p device_id:=amr_clock_lab \
  -p backend:=mock -p use_sim_time:=true
```

확인:
- ROS stamp는 초기 시각에 머물 수 있음.
- 예제 heartbeat와 mock 이동/timeout은 wall-time 정책에 따라 진행.
- 따라서 stamp만 보고 프로세스가 정지했다고 단정하면 안 됨.

이 구성은 clock 준비 실패를 배우는 실험이며 정상 Isaac 운용 모드가 아닙니다.

## 8. 고급·운영 고려사항

- command watchdog은 상위 서버뿐 아니라 명령 실행부에도 둡니다.
- 늦게 도착한 명령을 걸러내려면 Twist처럼 stamp 없는 타입만으로는 한계가 있습니다.
  운영 확장에서는 stamped command, sequence, epoch, freshness 규칙을 검토합니다.
- SROS2·접근 제어·인증은 고급 검토 대상이며 이 코드에 구현되지 않았습니다.
- CPU 집약 작업을 콜백에 넣기 전에 분리 프로세스/C++ 전환 여부를 측정합니다.
- depth를 크게 늘려 버퍼만 키우면 오래된 제어 데이터가 실행될 수 있습니다.
- QoS deadline/liveliness와 업무 timeout을 같은 의미로 취급하지 않습니다.

## 9. 완료 기준

- [ ] QoS 불일치를 재현하고 수정했다.
- [ ] Action 실행 중에도 cancel 처리 경로가 살아있는 이유를 설명한다.
- [ ] wall-time watchdog이 sim pause와 독립인 이유를 설명한다.
- [ ] publisher 존재와 데이터 freshness를 구분한다.

## 10. 질문과 해설

**Q. MultiThreadedExecutor로 바꾸면 자동으로 해결되나요?**  
아니요. 콜백 그룹·잠금·CPU 작업·대기 구조가 함께 맞아야 합니다.

**Q. `/clock`이 멈추면 무조건 시뮬레이터 프로세스가 죽은 건가요?**  
pause, Clock publisher 중단, 통신 문제 등 여러 원인이 가능합니다. 별도 health 신호가 필요합니다.

**Q. reliable publisher와 best-effort subscriber는 항상 실패하나요?**  
그렇게 단순화하면 안 됩니다. requested/offered 호환성의 방향이 중요합니다. 실제 endpoint QoS와 공식 표를 확인합니다.[R4]

## 다음 단계
[Session 05](05_multi_robot_launch.md).

## 참고
[R3, R4, R5] 및 접근 제약: [SOURCES](../appendices/SOURCES.md).
