# 예제 인터페이스 계약 v0.1

이 계약은 본 테스트베드용 초안이며 실제 벤더/산업 표준이 아닙니다.
대상 제어기가 자체 ROS 인터페이스를 제공하면 그 정의를 우선 적용하세요.

## 현재 제공
- `/<device_id>/move_to`: `testbed_interfaces/action/MoveTo`
- `/<device_id>/state`: `testbed_interfaces/msg/DeviceState`
- 장비 하나당 동시에 한 작업만 허용. 새 작업은 실행 중이면 거부.
- 예제 좌표는 공통 2D map 프레임 기준 미터. 회전·TF는 없음.
- 상태 Topic: Reliable / Volatile / KeepLast(10), 기본 5 Hz.
- Action의 목표/결과/피드백 QoS는 rclpy 기본값. 모든 인터페이스를 같은 QoS로 강제하지 않음.

## 작업 수명주기
IDLE → RUNNING → SUCCEEDED / CANCELED / FAILED.
종료 상태는 다음 작업까지 유지합니다.
새 command_id를 사용하면 종료 상태에서 다시 시작할 수 있습니다.
실패 후 별도 복구 절차는 현재 생략되어 있습니다.

## 중복 요청
프로세스 메모리에서 command_id를 저장하고 재사용을 거부합니다.
이것은 결과 재전송형 멱등 API가 아닙니다.
메모리는 재시작 시 사라지고 캐시 크기도 제한되지 않으므로,
장시간 테스트 이전에 TTL/크기 제한·저장소 정책을 구현해야 합니다.

## 거부/오류
- 목표 거부: busy, 빈 ID, NaN/Inf 좌표, 중복 ID
- 목표 거부 시 Action result 본문은 없으며 ROS goal accepted=false를 확인합니다.
- `CANCELED`: 취소로 작업 종료
- `INJECTED`: fail_after_s에 따른 강제 실패
- `INTERNAL`: 내부 예외
- `SHUTDOWN`: 처리 중 종료 시 가능한 범위의 실패 반환
- 클라이언트와 서버 통신 단절 시 terminal result 전달 자체는 보장하지 않습니다.

## 취소/완료 경합
예제 실행 루프의 한 회차에서는 취소 관측 → 장애 주입 → 완료 판정 순서입니다.
실제 도착 결과가 먼저 확정된 뒤의 취소는 성공을 되돌리지 않습니다.
ROS cancel 응답은 정지 완료와 같지 않으며 최종 Action 상태를 확인해야 합니다.

## 상태/로그
state.stamp는 현재 mock에서 ROS wall clock입니다.
run_id는 실행 식별자이며 명령 ID와 별개입니다.
state.command_id는 최근 실행된 명령을 나타냅니다.
accept 직후 execute 시작 전까지 상태에 이전 명령이 잠깐 보일 수 있으므로
접수 판정은 Action goal 응답을 기준으로 합니다.
작업 이벤트는 JSON을 포함한 ROS 로그로 출력하며 전체 stdout 자체가 JSONL은 아닙니다.

## 향후 내부 Isaac 인터페이스
제안: cmd_vel(Twist), odom(Odometry), clock(Clock).
실제 로봇 모델과 컨트롤러에 맞춰 확정해야 하며 현재 구현되지 않았습니다.
협동로봇 ExecuteTask.action은 계약 초안만 있고 서버가 없습니다.
