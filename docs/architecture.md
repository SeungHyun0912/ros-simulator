# 아키텍처와 책임 경계

## 범위
통합 관리 시스템·Adapter는 외부 개발 대상입니다.
이 저장소는 가상 장비 서버와 시뮬레이션 실행 영역을 제공합니다.
기준 목표는 AMR 10대 + 협동로봇 5대이며, 현재 구현은 AMR 경량 예제까지입니다.

## 데이터 흐름
외부 Adapter → ROS MoveTo Action → AMR 가상 제어기 → MotionBackend
→ (현재) MockMotion / (후속) Isaac cmd_vel·odom 연결

DeviceState Topic과 Action feedback/result는 제어기에서 외부로 반환합니다.
ROS 2 제어기와 Isaac Sim은 별도 프로세스·실행 환경으로 구성합니다.

## 의존성 방향
- interfaces: 도메인 계약만 정의
- backends: ROS 비의존 MockMotion과 Backend 프로토콜
- devices: 상태 머신 + ROS I/O
- bringup: fleet에서 장비별 ROS 프로세스 생성
- scenarios: 외부 클라이언트와 테스트 제어
- isaac_sim: 시뮬레이션 엔진·씬·Bridge 구현 위치

`DeviceController`는 rclpy/Isaac 모듈을 import하지 않습니다.
실제 Isaac backend는 이 공통 상태 머신에 주입할 실행 구현입니다.
현재 `IsaacMotion`은 NotImplementedError로 실패하여 가짜 연동 성공을 방지합니다.

## 두 실행 모드
- mock: 벽시계 진행, 직선 위치 보간, GPU/센서/물리 없음
- isaac: 후속 구현. 시뮬레이션 Clock 기반 동작, 실제 위치 기반 완료

현재 mock을 다중 로봇 내비게이션으로 간주하지 않습니다.
AMR끼리 겹칠 수 있고 경로 충돌·교통 관제·안전 정지는 검증하지 않습니다.

## 프로세스 배치
초기에는 ROS 장비 1개당 프로세스 1개입니다.
10대 AMR 실행도 성능 보장이 아니라 설정 확장 예제입니다.
성능 측정에는 외부 Adapter와 시뮬레이터의 CPU/GPU 경쟁을 분리하고,
제어기 처리 시간과 Adapter 왕복 시간을 구분하세요.

## 시간
현재 mock은 use_sim_time=false만 지원합니다.
Isaac 연결 시 동작 시간은 ROS sim time, 통신 watchdog은 monotonic wall time으로 분리합니다.
Clock 정지/점프/리셋은 별도 테스트 대상입니다. Clock 발행자는 하나만 둡니다.

## 원본 설정
fleet 파일은 장비 ID·namespace·초기 위치의 원본입니다.
현재 mock launch가 이를 읽습니다. 후속 Isaac 씬 생성기도 동일 파일을 읽도록 구현하세요.
실행 프로필 YAML은 아직 로더가 없는 설계 참고 자료입니다.

## 인터페이스 변경
외부 Action/Topic의 타입·단위·오류 의미를 변경하면 docs/interfaces.md와
계약 테스트를 함께 수정합니다. 내부 backend 변경은 외부 계약에 전파하지 않습니다.
