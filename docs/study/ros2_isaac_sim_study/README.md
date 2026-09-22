# ROS 2 · Isaac Sim: Adapter 검증 환경 개발 스터디

이 자료는 통합 관리 시스템과 Adapter를 **별도로 개발**하는 개발자를 위한 실습 교재입니다.
목표는 로봇 제어 알고리즘 개발이 아니라 **ROS 2 가상 장비를 통한 Adapter 기능·성능 검증**입니다.
최종 설계 목표는 AMR 10대·협동로봇 5대이며, 제공 코드가 그 전체 시스템의 완성본이라는 뜻은 아닙니다.

- 자료 기준일: **2026-09-21 KST**. 도구의 현재 시각을 측정한 값은 아닙니다.
- ROS 실습 기준: Ubuntu 24.04 + ROS 2 Jazzy, Python 노드.
- Isaac Sim: 설치 버전을 먼저 확정하십시오. `latest` 문서를 영구 버전 잠금으로 사용하지 않습니다.
- 현재 대화에서 이전에 제공된 ZIP/MD의 실제 파일은 확인할 수 없어, **앞서 합의한 커리큘럼을 토대로 독립 학습 패키지**를 구성했습니다. 기존 저장소 파일을 검토·수정한 결과물은 아닙니다.
- 프로젝트별 설계, 임계값, 상태 머신, API는 학습용 제안이며 벤더 표준이 아닙니다.

## 1. 학습 순서

| 세션 | 내용 | 예상 순수 실습 시간* | 산출물 |
|---|---|---:|---|
| [00](sessions/00_environment_and_scope.md) | 환경·검증 경계·버전 관리 | 2~3h | 환경 매니페스트 |
| [01](sessions/01_ros_graph_workspace.md) | 노드·워크스페이스·빌드·진단 | 2~3h | 패키지 빌드 |
| [02](sessions/02_topics_services_state.md) | Topic·Service·상태·복구 | 3~4h | 상태 관찰·리셋 |
| [03](sessions/03_actions_and_mock_amr.md) | Action·이동·취소·중복 요청 | 4~6h | 경량 AMR |
| [04](sessions/04_qos_concurrency_time.md) | QoS·실행기·시계·watchdog | 3~5h | 장애 분석 기록 |
| [05](sessions/05_multi_robot_launch.md) | Namespace·Launch·다중 장비 | 3~4h | AMR 10대 경량 실행 |
| [06](sessions/06_isaac_scene_physics.md) | USD·물리·Standalone·Headless | 3~5h | 단일 물리 씬 |
| [07](sessions/07_bridge_closed_loop.md) | Bridge·Clock·명령/피드백 | 4~6h | AMR 프록시 폐루프 |
| [08](sessions/08_cobot_equipment_handover.md) | 협동로봇·PLC 모델·인터록 | 4~6h | 인계 계약·스키마 |
| [09](sessions/09_test_automation_metrics.md) | 테스트·로그·성능·장애 | 3~5h | 테스트 결과 보고서 |
| [10](sessions/10_advanced_operations_capstone.md) | 고급 기술·운영·최종 프로젝트 | 6~10h | 10대+5대 확장 설계 |

\* 작성자의 학습 계획 추정치입니다. 설치 장애 해결, 실제 협동로봇 서버·모델 구현 시간은 별도입니다.
선행 세션 완료 기준을 만족한 뒤 다음 세션으로 이동하십시오.

## 2. 자료 구조

```text
ros2_isaac_sim_study/
├── README.md
├── sessions/                  # 단계별 교재: 개념·코드·실습·주의·운영·퀴즈
├── appendices/                # 빠른 실행, 인터페이스, 운영, 출처, 검증 상태
├── examples/
│   ├── ros2_ws/src/
│   │   ├── study_interfaces/  # DeviceState, MoveTo, RunProgram 스키마
│   │   └── study_nodes/       # AMR server/client/watch, launch, 순수 로직 테스트
│   ├── isaac_sim/             # 물리 큐브, kinematic AMR bridge 예제
│   └── pure_python/           # 인터록 데모, 지표 집계
├── configs/                   # 설계용 목표/시나리오 YAML (자동 실행기 아님)
├── scripts/                   # 순수 Python 테스트/문법 검사
├── artifacts/                 # 실제 실행 결과용; Git 제외
└── requirements-study.txt
```

## 3. 코드 검증 등급

| 등급 | 의미 | 해당 항목 |
|---|---|---|
| A | 이 작성 환경에서 실제 실행한 순수 Python 테스트 | 상태 머신·인터록·집계: **27개 테스트 통과** |
| B | 문법 검사만 수행; ROS 런타임 실행하지 않음 | Action 서버/클라이언트·Launch·상태 감시 |
| C | 문법 검사만 수행; GPU·Isaac 설치 환경에서 확인 필요 | Isaac 씬·Bridge 예제 |
| D | 스키마/설계·확장 과제 | 협동로봇 Action 서버, PLC 프로토콜, 15대 통합 |

ROS 2, `colcon`, Isaac Sim, NVIDIA GPU는 작성 환경에서 사용하지 않았습니다.
따라서 “ROS 통신이 검증됨”, “로봇 15대가 실시간 동작함”을 주장하지 않습니다.
실제 검증 로그: [검증 보고서](appendices/VALIDATION.md).

## 4. 빠르게 시작

1. 이 디렉터리 자체를 VS Code에서 열거나, 기존 저장소의 별도 학습 디렉터리에 추가합니다.
2. [00 환경](sessions/00_environment_and_scope.md)을 먼저 읽습니다.
3. GPU 없이 시작하려면 [빠른 실행](appendices/QUICKSTART.md)의 순수 Python 단계를 실행합니다.
4. ROS가 준비되면 경량 AMR Action을 확인합니다.
5. 그 다음에만 Isaac 씬과 Bridge를 추가합니다.

기존 `study_nodes` 또는 같은 ROS 패키지 이름이 있으면 중복해서 overlay하지 마십시오.
이 패키지를 기존 repo에 옮길 때는 경로와 패키지 충돌을 먼저 검토합니다.

## 5. 공통 안전·해석 원칙

- 교육 코드는 **실제 로봇·실제 PLC에 연결하지 않습니다**. 별도 시험망과 ROS Domain을 사용합니다.
- ROS Domain ID는 이름 공간/발견 분리용이지 인증·암호화 경계가 아닙니다.
- `SetBool` 테스트 장애 플래그는 비상정지나 안전 제어가 아닙니다.
- `mock` 이동은 충돌 없는 평면 운동입니다.
- Isaac `kinematic` 프록시도 휠·접촉 물리를 검증하지 않습니다.
- Action 취소 수락과 실제 정지 확인은 다른 사건입니다.
- Adapter 검증을 통과해도 실제 로봇 제어기·PLC·안전 기능의 인증을 대신하지 못합니다.

## 6. 기술 자료와 출처

검증 경계·과제·코드는 본 교재의 설계입니다. 외부 기술 사실은 각 세션의 출처 번호로 구분했습니다.
공식 문서 확인 결과와 접근 실패 항목은 [SOURCES](appendices/SOURCES.md)에 기록했습니다.
특히 기존 대화의 **Isaac Sim 5.1 고정 가정은 신규 설치 권고로 사용하지 않습니다**. 확인한 5.1 문서에는 지원 종료 안내가 있으며, 설치할 지원 버전의 문서와 런타임을 다시 맞춰야 합니다.[I0]

## 최종 학습 방향

**경량 장비 계약을 먼저 검증 → Isaac 결과로 상태를 결정 → 다중 장비·장애·운영 검증** 순서로 진행합니다.
