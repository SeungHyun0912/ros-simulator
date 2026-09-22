# 학습용 인터페이스 계약 v0.1

이 문서는 벤더 표준이 아닌 자체 학습 계약입니다.
실제 Adapter 계약이 이미 있으면 그 정의를 우선하며 이 예제를 교체합니다.

## ROS endpoint

| 경로 | 종류/타입 | 제공 여부 |
|---|---|---|
| `/<device>/state` | Topic / study_interfaces/DeviceState | 구현 |
| `/<device>/move_to` | Action / study_interfaces/MoveTo | AMR 구현 |
| `/<device>/reset_idle` | Service / std_srvs/Trigger | 구현 |
| `/<device>/test/set_fault` | Service / std_srvs/SetBool | 테스트 전용 구현 |
| `/<device>/cmd_vel` | Topic / geometry_msgs/Twist | odom backend에서 발행 |
| `/<device>/odom` | Topic / nav_msgs/Odometry | odom backend에서 구독 |
| `/clock` | Topic / rosgraph_msgs/Clock | Isaac 예제에서 하나만 발행 |
| `/<cobot>/run_program` | Action / study_interfaces/RunProgram | 스키마만 제공 |

## 단위·프레임

- 좌표: meter, 목표는 공통 `map` 평면 좌표.
- 속도: m/s, 회전속도 rad/s.
- odom 예제는 추정 오도메트리가 아니라 **프록시 ground truth**를 발행합니다.
- 제공된 AMR 서버는 프레임 변환을 수행하지 않습니다.
- 따라서 다른 frame의 odom/goal을 연결하면 오동작할 수 있습니다.
- 실제 확대 시 frame_id 확인, tf2 변환, yaw 목표, 정지 확인을 추가하십시오.

## Action 동작

- 1대당 동시 활성 작업 최대 1개. BUSY면 거부.
- 같은 tick에서 처리 우선순위: 관측된 취소 → 주입 장애 → pose stale → timeout → 도착.
- 완료 판정: XY 거리 0.03m 이하. 최종 자세와 속도는 이 단계에서 확인하지 않음.
- mock: 이상적인 평면 직선 이동; 물리 검증 아님.
- odom: 수신 위치 기반 도착. 단순 heading follower; 장애물 회피 없음.
- 취소 terminal 전 0 속도를 발행하지만, 실제 감속·정지 확인을 기다리지는 않음.
- result retention: 서버 60초 설정. 영구 작업 조회 저장소가 아님.
- 동일 task_id 재요청: 프로세스 내 저장된 1024개까지 중복 거부.
- ledger 가득 참: 신규 요청 거부. 무조건 오래된 키를 지우지 않음.
- 서버 재시작: ledger 소실, boot_id 변경. 재시작 간 멱등성 미구현.
- 서비스 reset: 작업 비활성 조건에서 상태만 IDLE. 위치·중복 ledger는 유지.
- 서버 로그에는 거부 사유가 남지만 Action reject 자체에는 사용자 정의 상세 사유가 없음.
  거부 사유 조회 API는 운영 확장 과제.

## 시간

- task timeout / pose watchdog / command watchdog: host monotonic clock.
- state stamp: 노드 ROS clock (`use_sim_time=true`면 시뮬레이션 Clock).
- simulation pause가 wall-time timeout을 멈추지 않음. 의도된 테스트 정책.
- 다른 host의 monotonic timestamp끼리 차감 금지.
- Clock 초기값 0을 준비 완료로 오해하지 말 것.

## 장애 모델과 한계

SetBool true는 작업 실패/신규 거부를 주입합니다.
패킷 손실·전원 차단·안전 PLC·실제 통신 장애를 구현하지 않습니다.
DDS Reliable은 업무 명령의 exactly-once 실행 증명이 아닙니다.
프로세스 종료, 응답 유실 시 결과 UNKNOWN을 유지하고 상태·작업 이력을 확인해야 합니다.

## 버전 정책 제안

필드 삭제·타입 변경·단위 변경·오류 의미 변경은 계약 변경으로 관리합니다.
재시작/중복/취소 경합 테스트를 계약 버전별 회귀 세트로 유지하십시오.
