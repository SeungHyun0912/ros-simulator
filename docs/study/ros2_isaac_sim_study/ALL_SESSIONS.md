# ROS 2 · Isaac Sim Adapter 검증 스터디 — 전체 세션

세션별 파일과 코드가 포함된 ZIP을 먼저 압축 해제하십시오. 이 통합본의 상대 링크는 압축 해제된 루트 기준입니다.
검증 상태: 순수 Python 27개 테스트 통과; ROS/Isaac 실행 미검증.



---

원본: `README.md`

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



---

원본: `sessions/00_environment_and_scope.md`

# Session 00 — 검증 경계·환경·버전 관리

> 난이도: 입문 / 예상 2~3시간 / GPU: 불필요
> 선행: Python 함수·클래스, Linux 터미널의 기본 사용

## 1. 이 세션의 목표

학습을 시작하기 전에 “무엇을 통과시키려는 테스트인가”를 한 문장으로 정의합니다.

> 실제 Adapter가 ROS 2 가상 장비와 명령·상태·취소·오류를 올바르게 교환하는지 검증한다.

로봇 내비게이션 알고리즘, 모터 드라이버, 안전 제어, 실제 PLC scan cycle의 정밀 재현은 이번 기본 과정의 목표가 아닙니다.
같은 화면에서 AMR이 움직여도 작업 ID가 잘못 매핑되면 Adapter 테스트는 실패입니다.
반대로 화면이 없어도 명령 변환과 타임아웃 검증은 가능합니다.

## 2. 전체 구조를 읽는 방법

```text
[별도 repo] 통합 관리 시스템 / 테스트 실행기
       |
[별도 repo] Adapter (System Under Test)
       | 외부 ROS 계약: Action / Topic / Service
[이 학습 repo] 가상 장비 상태 머신
       | 내부 실행 경계
       +---- mock: 시간/상태 기반
       |
       +---- odom: cmd_vel → Isaac → odom
```

- **SUT**: 테스트 대상 Adapter.
- **Test double**: 실제 장비를 대신하는 가상 서버.
- **Oracle**: 올바른 결과인지 판단하는 기준. Adapter 구현에서 그대로 복사하지 않고 장비 계약에서 정의합니다.
- **Backend**: 움직임을 계산하거나 실제 시뮬레이션에 전달하는 실행부.
- **Scenario**: 입력·장애·예상 결과를 묶은 테스트.

본 과정의 폐루프 예제는 ROS 노드의 업무용 Action과 Isaac 내부 표준 메시지를 분리합니다.
복잡한 사용자 정의 Action을 Isaac 프로세스 안으로 넣지 않는 것이 초기 설계 원칙입니다.

## 3. 버전 조합 선택

실습은 Ubuntu 24.04 + ROS 2 Jazzy를 기준으로 작성했습니다.
Isaac 공식 설치 문서에도 이 조합의 경로가 제시되어 있습니다.[I1]

다만 다음을 혼동하지 마십시오.

1. Ubuntu에서 실행하는 ROS Python.
2. Isaac Sim이 사용하는 Python.
3. 단위 테스트용 venv.
4. VS Code가 코드 분석에 사용하는 interpreter.

프로세스 간 ROS 메시지 통신은 Python 모듈을 서로 직접 import하는 것과 다릅니다.
사용자 정의 ROS Python 모듈을 Isaac 안에 직접 import한다면 ABI와 빌드 환경을 별도로 맞춰야 합니다.[I1]

**버전 고정 작업**
- 실제 설치한 Isaac 릴리스와 문서 URL을 기록합니다.
- `latest` URL만 기록하지 말고 지원되는 버전 문서가 있으면 함께 기록합니다.
- 5.1 보관 문서에는 지원 종료 안내가 있으므로 신규 설치의 기본값으로 고정하지 않습니다.[I0]

## 4. 실습 A — 환경 매니페스트 작성

[ENVIRONMENT_MANIFEST.yaml](appendices/ENVIRONMENT_MANIFEST.yaml)을 복사하여 관측값을 채웁니다.

```bash
uname -a
python3 --version
nvidia-smi
```

ROS 설치 후:

```bash
source /opt/ros/jazzy/setup.bash
printenv ROS_DISTRO
ros2 doctor --report
```

명령이 없으면 설치/경로 문제로 기록합니다. 없는 도구의 버전을 추측해서 채우지 않습니다.
GPU가 없는 개발 PC에서는 `nvidia-smi` 실패가 정상일 수 있습니다.

## 5. 실습 B — GPU 없이 상태 모델 실행

루트에서:

```bash
python3 -m venv .venv-study
source .venv-study/bin/activate
python -m pip install -r requirements-study.txt
export PYTHONPATH="$PWD/examples/ros2_ws/src/study_nodes"
python - <<'PY'
from study_nodes.core import Motion, Request
m = Motion()
m.start(Request("s00-task", 0.3, 0.0, speed=0.3))
for _ in range(30):
    m.tick(0.05)
print(m.phase, round(m.x, 3), m.detail)
PY
```

기대 조건: `SUCCEEDED`와 `ARRIVED`. 이는 물리적 주행 성공이 아니라 상태 모델의 이동 완료입니다.

### 코드 해설

- `Request`: 작업의 입력 계약.
- `Motion`: 현재 위치와 작업 상태를 가진 순수 Python 객체.
- `tick(dt)`: 외부에서 시간을 주입하므로 실제 1초를 기다리지 않고 테스트 가능.
- timeout 기준은 입력 `dt`의 누적이며, ROS 서버는 이를 host monotonic 시간으로 공급합니다.

## 6. 자주 하는 실수

| 증상 | 먼저 확인 |
|---|---|
| 시스템 Python에서 Isaac import 실패 | Isaac용 실행기를 사용했는가 |
| 생성한 ROS 메시지 import 실패 | 빌드 후 workspace source를 했는가 |
| VS Code만 빨간 줄 | editor interpreter와 실제 실행 환경이 다른가 |
| 예전 버전 코드 import 경로 오류 | 보관 문서와 설치 버전이 다른가 |
| 작업 완료인데 화면에 변화 없음 | mock backend인지 확인 |

## 7. 고급·운영 고려사항

- 별도 Python 프로세스 간 통신으로 ABI 결합을 줄입니다.
- CI에는 GPU 없는 빠른 테스트와 GPU 필요한 통합 테스트를 나눕니다.
- 설치 전후의 의존성 lock·컨테이너 이미지 digest·드라이버를 기록합니다.
- GPU 서버 한 대의 성능이 충분한지는 장비 수만으로 판정하지 않습니다.
- 초기 목표 10대+5대는 설계 목표이며 이 교재의 실측 처리 용량이 아닙니다.

## 8. 완료 기준

- [ ] 테스트 대상과 대역 장비를 그림 없이 말로 구분한다.
- [ ] 실제 관측한 환경 정보를 매니페스트에 기록했다.
- [ ] 순수 Python 상태 모델을 실행했다.
- [ ] mock 완료와 물리 완료의 차이를 설명한다.
- [ ] 실제 설비망에 연결되지 않았음을 확인했다.

## 9. 확인 질문과 해설

**Q1. 모든 코드를 같은 venv에 넣으면 관리가 쉬워지지 않나요?**  
버전이 다른 ROS/Isaac Python 의존성을 섞는 위험이 있습니다. 같은 저장소와 같은 런타임은 별개입니다.

**Q2. 이 과정에서 개발할 것은 Adapter인가요?**  
아닙니다. Adapter에 연결할 가상 장비와 테스트 도구입니다. client 예제는 Adapter 대역으로 학습에만 사용합니다.

**Q3. mock에서 성공한 동작을 실제 로봇에서도 성공으로 볼 수 있나요?**  
아니요. 계약과 논리의 일부만 확인한 것입니다. 물리·벤더·안전 검증은 별도입니다.

## 다음 단계
[Session 01](sessions/01_ros_graph_workspace.md)에서 실제 ROS 패키지를 빌드합니다.

## 참고
[I0, I1]의 원문과 확인 범위: [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/01_ros_graph_workspace.md`

# Session 01 — ROS Graph·패키지·워크스페이스·진단

> 난이도: 입문 / 예상 2~3시간 / GPU: 불필요
> 선행: Session 00, ROS 2 Jazzy 설치

## 1. 핵심 개념

이 교재의 장비 1대는 하나의 독립 ROS 노드 프로세스로 실행합니다.
노드 이름은 `amr_server`, Namespace는 `/amr_01`처럼 장비 ID를 반영합니다.
Topic, Service, Action은 그 노드가 제공하거나 사용하는 통신 endpoint입니다.[R1]

예를 들어 상대 이름 `state`를 `/amr_01` Namespace 안에서 생성하면 실제 endpoint는 `/amr_01/state`가 됩니다.
프로젝트 규칙상 장비 endpoint에는 상대 이름을 사용하고, `/clock`만 공용 절대 이름으로 둡니다.

**용어를 구분하십시오.**
- 패키지: 빌드·배포 단위.
- workspace: 여러 패키지를 빌드하는 작업 공간.
- 노드: ROS 실행 구성 요소.
- 프로세스: OS 실행 단위. 패키지와 노드 수가 반드시 같지 않습니다.
- launch: 여러 실행 프로세스와 파라미터를 구성하는 진입점.

위 구분을 바탕으로 본 교재는 장비별 별도 프로세스를 우선합니다.

## 2. 제공 패키지의 역할

```text
examples/ros2_ws/src/
├── study_interfaces/
│   ├── msg/DeviceState.msg
│   ├── action/MoveTo.action
│   ├── action/RunProgram.action
│   ├── CMakeLists.txt
│   └── package.xml
└── study_nodes/
    ├── study_nodes/
    ├── launch/
    ├── test/
    ├── setup.py
    ├── setup.cfg
    └── package.xml
```

`study_interfaces`는 인터페이스를 생성하는 ament_cmake 패키지,
`study_nodes`는 Python 실행 코드를 제공하는 ament_python 패키지입니다.
본 구성의 ROS 빌드는 아직 작성 환경에서 실행하지 않았으므로 실제 Jazzy에서 검증합니다.

## 3. 코드 읽기 — 실행 파일은 어디서 등록되나요?

`study_nodes/setup.py`의 다음 설정이 CLI 이름과 Python 함수를 연결합니다.

```python
entry_points={"console_scripts": [
    "amr_server = study_nodes.amr_server:main",
    "move_client = study_nodes.move_client:main",
    "state_watch = study_nodes.state_watch:main",
]}
```

따라서 `ros2 run study_nodes amr_server`는 `amr_server.py`의 `main()`을 호출합니다.
`setup.cfg`는 ROS 실행 파일이 설치될 패키지별 경로를 지정합니다.
이 파일들을 생략하고 Python 코드만 복사하면 `ros2 run`이 찾지 못할 수 있습니다.

## 4. 실습 — 빌드와 source

루트 경로를 지정하고 ROS 환경이 준비된 새 터미널에서 실행합니다.

```bash
export STUDY_ROOT=/absolute/path/to/ros2_isaac_sim_study
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd "$STUDY_ROOT/examples/ros2_ws"
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --symlink-install
source install/setup.bash
ros2 pkg executables study_nodes
ros2 interface show study_interfaces/msg/DeviceState
```

기대 조건:
- 3개 console script 이름을 찾을 수 있음.
- DeviceState의 device_id·boot_id·sequence 필드 확인.
- RunProgram은 스키마가 보이더라도 서버가 구현된 것은 아님.

별도 터미널도 같은 ROS와 workspace를 source해야 합니다.

## 5. 실습 — ROS Graph 관찰

터미널 A:

```bash
ros2 run study_nodes amr_server --ros-args \
  -r __ns:=/amr_01 -p device_id:=amr_01
```

터미널 B:

```bash
ros2 node list
ros2 node info /amr_01/amr_server
ros2 topic list -t
ros2 service list -t
ros2 action list -t
```

기록할 항목:
1. 노드 이름과 Namespace.
2. `state` Topic의 타입.
3. `move_to` Action의 타입.
4. `reset_idle` Service의 타입.
5. 현재 명령하지 않아도 상태가 발행되는지.

`cmd_vel` publisher가 보인다는 사실만으로 로봇이 움직이거나 메시지를 보내고 있다고 판단하지 않습니다.
endpoint 존재와 메시지 흐름을 분리해서 관찰합니다.

## 6. 장애를 만드는 작은 과제

1. 터미널 B에서 Domain을 43으로 바꿉니다.
2. `ros2 daemon stop` 후 graph를 다시 관찰합니다.
3. Domain을 42로 복구하고 다시 확인합니다.

기대: 해당 환경에서 발견되는 그래프가 달라지는지 관찰합니다.
기존 daemon·네트워크·발견 지연 때문에 즉시 바뀌지 않을 수 있으므로 시간을 기록하십시오.

중요: 이 과제는 논리 분리를 배우는 것이며 보안 격리의 증명이 아닙니다.

## 7. 주의사항

- **같은 이름의 서버를 중복 실행하지 마십시오.** 결과 수신·진단이 혼란스러워질 수 있습니다.
- 인터페이스 `.msg`/`.action` 변경은 재빌드 대상입니다. symlink-install이 코드 생성까지 대신하지 않습니다.
- 이전 workspace의 overlay를 source한 터미널에서 다른 버전을 빌드하면 경로가 섞일 수 있습니다.
- `build/install/log`를 코드 원본으로 커밋하지 않습니다.
- rosdep 실패를 무시하고 “빌드 완료”로 기록하지 않습니다.

## 8. 고급·운영 고려사항

- 환경 로더 스크립트는 재실행해도 PATH가 무한 중첩되지 않게 관리합니다.
- 패키지별 버전과 외부 계약 버전을 구분합니다.
- 컨테이너 도입 전에 호스트 환경에서 1대의 통신을 먼저 확인합니다.
- headless 서버에서는 GUI 도구 없이 CLI만으로 최소 진단이 가능하도록 실행 절차를 문서화합니다.
- 사내 네트워크에서는 multicast·방화벽·DDS discovery 설정을 명시합니다. 설정값은 실제 RMW에 맞춰 확인합니다.

## 9. 완료 기준

- [ ] package, workspace, node, process를 구분한다.
- [ ] 두 패키지를 빌드하고 생성된 타입을 확인했다.
- [ ] 상대 endpoint와 Namespace의 관계를 설명한다.
- [ ] source 누락과 Domain 불일치를 진단했다.

## 10. 확인 질문

**Q. `ros2 topic list`에 나오면 데이터가 정상인가요?**  
아닙니다. endpoint 발견, 타입 일치, QoS, 실제 수신을 순서대로 확인합니다.

**Q. Python 중심인데 왜 CMake 패키지가 있나요?**  
여기서는 사용자 정의 인터페이스 생성과 Python 노드 실행을 분리했기 때문입니다.

**Q. 서버 10대는 패키지 10개가 필요한가요?**  
아닙니다. 같은 패키지를 Namespace·파라미터를 달리하여 실행합니다.

## 다음 단계
[Session 02](sessions/02_topics_services_state.md).

## 참고
[R1, R2] 및 Jazzy 인터페이스 문서 접근 상태: [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/02_topics_services_state.md`

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
[Session 03](sessions/03_actions_and_mock_amr.md).

## 참고
[R1, R5], [인터페이스 계약](appendices/INTERFACE_CONTRACT.md),
[SOURCES](appendices/SOURCES.md).



---

원본: `sessions/03_actions_and_mock_amr.md`

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
전체 계약: [INTERFACE_CONTRACT](appendices/INTERFACE_CONTRACT.md).

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
[Session 04](sessions/04_qos_concurrency_time.md).

## 참고
[R1, R2, R3, R6] 범위와 코드 검증 등급: [SOURCES](appendices/SOURCES.md), [VALIDATION](appendices/VALIDATION.md).



---

원본: `sessions/04_qos_concurrency_time.md`

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
[Session 05](sessions/05_multi_robot_launch.md).

## 참고
[R3, R4, R5] 및 접근 제약: [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/05_multi_robot_launch.md`

# Session 05 — Namespace·Launch·AMR 10대와 확장 구조

> 난이도: 중급 / 예상 3~4시간 / GPU: 불필요
> 선행: Session 04

## 1. 이 세션의 목표

AMR을 10번 복사해 서로 다른 코드를 만드는 것이 아니라, 같은 코드를 다른 장비 설정으로 실행합니다.
검증 대상은 “10대가 화면에 보이는가”가 아니라 **명령·상태·오류가 다른 장비로 섞이지 않는가**입니다.

이번 제공 Launch는 AMR 1~10대 mock만 실행합니다.
협동로봇 5대와 Isaac 모델 배치는 Session 08·10의 확장 과제입니다.

## 2. 장비 식별자·Namespace·Frame을 구분하기

| 항목 | 예 | 의미 |
|---|---|---|
| device_id | amr_01 | 업무 장비 식별 |
| Namespace | /amr_01 | ROS endpoint 접두 경로 |
| node name | controller | Namespace 안의 실행 노드 이름 |
| task_id | order-42-leg-1 | 업무 요청 식별 |
| boot_id | 프로세스 UUID | 재시작 경계 |
| frame | amr_01/base_link | 공간 좌표계 식별 |

Namespace를 붙였다고 메시지 안의 문자열 frame_id가 자동으로 바뀐다고 가정하지 않습니다.
이번 예제는 frame 이름을 명시적으로 만듭니다.
tf2 기반 실제 로봇 확장에서는 frame·tf 발행 주체·변환 트리를 별도 검증해야 합니다.

## 3. Launch 코드 읽기

실제 파일: `study_nodes/launch/fleet.launch.py`

```python
return [Node(
    package="study_nodes",
    executable="amr_server",
    namespace=f"amr_{i:02d}",
    name="controller",
    parameters=[{
        "device_id": f"amr_{i:02d}",
        "backend": "mock",
        "use_sim_time": False,
    }],
) for i in range(1, count + 1)]
```

장비마다 별도 프로세스를 실행하도록 구성했습니다.
이 단계에서는 RMW·Domain·환경 변수는 상위 터미널에서 명시하고 상속합니다.

왜 1..10으로 제한했을까요?
실수로 지나치게 많은 프로세스를 생성하지 않도록 한 교재용 guard입니다.
ROS 2의 최대 장비 수를 의미하지 않습니다.

## 4. 실습 A — 3대부터 10대로

기존 서버를 종료한 뒤:

```bash
ros2 launch study_nodes fleet.launch.py count:=3
```

다른 터미널:

```bash
ros2 node list
ros2 action list -t
ros2 topic info /amr_01/state --verbose
```

서버 node 이름이 `controller`로 바뀌므로 `/amr_01/controller`를 확인합니다.
단일 실행 예제의 `/amr_01/amr_server`를 그대로 기대하면 안 됩니다.

정상 동작 후 count:=10으로 확장합니다.

## 5. 실습 B — 두 장비에 동시 작업

```bash
ros2 run study_nodes move_client --ros-args \
  -r __ns:=/amr_01 -p x:=2.0 &
P1=$!
ros2 run study_nodes move_client --ros-args \
  -r __ns:=/amr_02 -p x:=3.0 &
P2=$!
wait "$P1" "$P2"
```

기대:
- 각 장비 상태에 자기 task_id만 표시.
- amr_01 완료가 amr_02 완료로 오인되지 않음.
- 두 작업이 동시 진행 가능.

이 shell 예시는 정상 병렬 실행 시연용입니다.
종료코드와 UNKNOWN을 개별 수집하는 완전한 부하 실행기는 Session 09의 확장 과제입니다.

## 6. 실습 C — 고장 격리

amr_01과 amr_02를 멀리 이동시킨 상태에서:

```bash
ros2 service call /amr_01/test/set_fault std_srvs/srv/SetBool "{data: true}"
```

합격 조건:
- amr_01만 실패.
- amr_02 작업은 지속.
- amr_01 fault를 해제하기 전 새 요청은 거부.
- 다른 장비의 state sequence·boot_id가 리셋되지 않음.

다음으로 amr_01 프로세스 종료와 전체 Launch 종료를 구분해서 실험합니다.
터미널에서 전체 Launch에 Ctrl+C 하면 모든 장비가 종료될 수 있으므로,
단일 프로세스 장애 실험은 대상 PID를 먼저 확인하고 **학습 프로세스만** 대상으로 합니다.

## 7. 설정 파일로 확장하는 과제

`configs/fleet_target.yaml`은 현재 **설계 입력 예시**이지 Launch가 읽는 파일이 아닙니다.
과제는 이 YAML을 읽는 loader를 추가하는 것입니다.

필수 검증:
- device_id와 Namespace 중복 금지.
- AMR/cobot 타입 허용 목록.
- backend 값 검증.
- 수량 상한·메모리 예상·잘못된 초기 위치 검사.
- 실행 전 전체 설정 검증 후 한 번에 실행.
- 실제 적용한 설정을 artifacts에 저장.

부분적으로 5대만 뜬 상태를 “10대 준비 완료”로 보고하면 안 됩니다.

## 8. 고급·운영 고려사항

**프로세스 분리와 통합의 비교 — 설계 판단**

| 구성 | 장점 | 비용/위험 |
|---|---|---|
| 장비당 프로세스 | 장애 격리·진단 단순 | 프로세스·DDS 자원 증가 |
| 여러 장비를 한 프로세스 | 공통 자원 활용 가능 | 예외·lock·CPU 병목이 다른 장비에 전파 |
| 여러 시뮬레이터 인스턴스 | 씬 분할·장애 범위 분리 | Clock·공유 공간·자원 동기화 복잡 |

이 교재는 첫 번째를 시작점으로 삼습니다. 성능을 측정하기 전 하나의 초대형 노드로 합치지 않습니다.

- 자동 respawn은 편리하지만 ledger 소실·새 boot_id를 감춥니다.
- 준비 완료는 “프로세스 시작”이 아니라 필수 endpoint·상태 freshness·모델 준비 조건으로 판정합니다.
- 여러 개발자의 테스트는 Domain뿐 아니라 네트워크·로그 디렉터리도 분리합니다.
- 여러 Isaac 실행에서 동일 `/clock`을 발행하지 않도록 합니다.

## 9. 완료 기준

- [ ] AMR 10대 mock endpoint를 고유하게 확인했다.
- [ ] 2대 동시 요청과 단일 장비 장애 격리를 확인했다.
- [ ] Namespace와 frame_id의 차이를 설명한다.
- [ ] YAML 설계 파일이 현재 실행기가 아니라는 점을 구분한다.

## 10. 질문과 해설

**Q. ROS 노드 10대면 Isaac 프로세스도 10개가 필요한가요?**  
아닙니다. 한 씬의 10개 장비와 ROS 프로세스 10개를 연결하는 설계가 가능합니다. 구체 구현과 성능 검증은 별도입니다.

**Q. 같은 task_id를 서로 다른 장비가 받아도 되나요?**  
키의 범위를 계약에서 정해야 합니다. 예제 ledger는 장비 프로세스별이며 시스템 전체 중복을 막지 않습니다.

**Q. 서버가 재시작하면 진행하던 작업을 자동 복구하나요?**  
제공 코드는 복구하지 않습니다. boot_id 변경과 UNKNOWN 처리 후 별도 조회·복구가 필요합니다.

## 다음 단계
[Session 06](sessions/06_isaac_scene_physics.md).

## 참고
노드/인터페이스 개념 [R1], 구현은 본 교재 제안. [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/06_isaac_scene_physics.md`

# Session 06 — Isaac Sim의 씬·물리·로봇·Standalone

> 난이도: 입문~중급 / 예상 3~5시간 / GPU: 필요
> 선행: Session 00 환경 확정, Session 05 권장
> 코드 등급 C: GPU/Isaac 환경에서 실행하지 않았음. 설치 버전 API 확인 필요.

## 1. 이번 목표

복잡한 창고 대신 바닥과 큐브 하나를 생성하고, reset→step→상태 읽기를 이해합니다.
같은 씬을 코드로 반복 생성할 수 있어야 자동 테스트의 출발점이 됩니다.

Isaac 문서는 Standalone에서 시뮬레이션 단계와 ROS 실행을 구성하는 흐름을 제공합니다.[I2]
예제의 World·큐브 구조는 Core API 보관 문서를 참고했으므로 설치 버전의 import/API를 먼저 확인하십시오.[I4]
특정 Isaac 신규 버전에서 실행된 코드라고 주장하지 않습니다.

## 2. 핵심 개념

아래 용어는 이 실습을 읽기 위한 최소 설명입니다.[I4]

- **Stage**: 씬 전체를 담는 USD 장면.
- **Prim**: 장면의 개별 요소와 경로.
- **Transform**: 위치·회전·크기.
- **Rigid body / Collision**: 물리 운동과 접촉 계산에 쓰는 설정.
- **Articulation**: 여러 관절로 연결된 로봇 구조.
- **Physics step**: 물리 상태를 갱신하는 단계.
- **Render**: 화면이나 렌더링 기반 센서 출력을 생성하는 작업.

기하가 보인다는 사실만으로 rigid body·충돌·관절 제어가 설정된 것은 아닙니다.

## 3. 제공 파일 구분

| 파일 | 역할 | 검증 범위 |
|---|---|---|
| `scene_smoke.py` | 중력 아래 동적 큐브 | 씬/물리 초기 실행 |
| `kinematic_amr_bridge.py` | ROS 속도 명령을 따르는 시각적 프록시 | 명령·피드백 폐루프 |
| 실제 AMR USD | 제공하지 않음 | 사용자 모델 또는 공식 에셋으로 확장 |
| 실제 협동로봇 USD | 제공하지 않음 | 후속 과제 |

외부 로봇 모델 다운로드·라이선스 문제를 기본 첫 실습에서 분리한 구성입니다.

## 4. 코드 해설 — 초기화 순서

파일: `examples/isaac_sim/scene_smoke.py`

```python
from isaacsim import SimulationApp
app = SimulationApp({"headless": args.headless})

# Isaac-dependent imports are after application initialization.
from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid

world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()
```

설치판에 해당 module/class가 없으면 이전 이름을 무작위로 섞지 말고 설치 버전 API를 확인합니다.
GUI Script Editor에 그대로 붙여 넣는 코드는 아닙니다. 이미 실행 중인 앱 안에서 SimulationApp을 다시 만드는 방식을 사용하지 마십시오.

큐브 생성:

```python
cube = world.scene.add(DynamicCuboid(
    prim_path="/World/TestBox",
    name="test_box",
    position=np.array([0.0, 0.0, 1.0]),
    size=0.2,
))
world.reset()
world.step(render=True)
```

설정 의미:
- 초기 높이 1m.
- 한 변 0.2m 큐브.
- 미터 단위 씬.
- `reset` 후 물리 상태를 초기화하고 step 진행.

정확한 최종 높이를 엔진 버전과 무관한 고정값으로 단정하지 않고 실제 관측합니다.

## 5. 실습 A — GUI 실행

세션 00의 환경과 공식 설치 문서를 확인한 별도 터미널에서:

```bash
export ISAAC_SIM_ROOT=/absolute/path/to/isaac-sim
export STUDY_ROOT=/absolute/path/to/ros2_isaac_sim_study
"$ISAAC_SIM_ROOT/python.sh" \
  "$STUDY_ROOT/examples/isaac_sim/scene_smoke.py" --steps 300
```

확인:
- 앱이 시작되는가?
- 큐브가 지면 방향으로 움직이는가?
- 종료 시 final position이 출력되는가?
- 프로세스가 정상 종료되는가?

300 physics step은 벽시계 300초가 아닙니다. step과 실제 경과시간을 구분합니다.

## 6. 실습 B — Headless 비교

```bash
"$ISAAC_SIM_ROOT/python.sh" \
  "$STUDY_ROOT/examples/isaac_sim/scene_smoke.py" \
  --headless --steps 300
```

비교 항목:
- 앱 시작·에셋 로딩 시간
- step 처리 시간
- GPU/VRAM 사용량
- 최종 상태

예제는 `render=False`로 step합니다.
하지만 Headless/해당 옵션만으로 앱 내부의 모든 렌더링 경로가 제거됐다고 보장하지 않습니다.
Viewport·센서·streaming 설정은 별도 확인 대상입니다.[I3]

첫 실행의 shader compilation·캐시 생성 비용을 steady-state 처리량과 섞지 마십시오.

## 7. 로봇 모델로 넘어갈 때

**AMR 체크리스트 — 프로젝트 제안**
- 바퀴 joint 이름과 순서.
- wheel radius·wheel base와 단위.
- chassis articulation root.
- 충돌 형상이 바퀴와 바닥을 올바르게 처리하는가.
- 초기 자세에서 바닥을 관통하거나 떠 있지 않은가.
- 속도 명령→휠 명령 변환 위치.

**협동로봇 체크리스트**
- joint names/limits, base/tool frame.
- gripper와 장착 위치.
- trajectory 목표와 실제 joint feedback.
- 작업대·화물 충돌.
- 그리퍼 닫힘과 실제 화물 소유권 변경의 구분.

이 교재의 목표는 이 모든 제어를 직접 개발하는 것이 아닙니다.
공식 예제나 검증된 controller를 연결하되 Adapter 계약은 유지하는 것이 확장 방향입니다.

## 8. 주의사항

- 비주얼 메시와 충돌 메시를 혼동하지 않습니다.
- 실제 질량·마찰·관성 값이 없으면 임의값임을 매니페스트에 표시합니다.
- 로봇을 매 step teleport하는 방식으로 충돌 회피가 검증됐다고 주장하지 않습니다.
- 위치·관절 feedback 없이 타이머만 끝났다고 SUCCESS를 보내지 않습니다.
- 씬 경로와 에셋 버전을 코드 안에 개인별 절대경로로 고정하지 않습니다.
- physics reset 뒤 기존 핸들/캐시가 유효한지는 설치 API에서 확인합니다.

## 9. 고급·운영 고려사항

- Isaac extension 방식은 GUI 도구가 필요할 때 추가하고, 자동 테스트는 Standalone부터 시작합니다.
- 큰 USD/텍스처는 Git 본문 대신 에셋 저장소와 해시로 관리하는 정책을 검토합니다.
- 렌더링·물리·ROS publish 주기는 각각 측정합니다.
- 시뮬레이터 내부에서 DDS callback이 직접 USD를 수정하는 멀티스레드 구조는 피하고,
  요청 큐를 통해 simulation thread에서 적용하는 패턴을 검토합니다.
- 이 예제 Bridge는 단일 스레드에서 spin_once와 씬 업데이트를 수행합니다.
- 같은 seed로도 하드웨어·solver·병렬 실행에 따라 결과가 달라질 수 있으므로 허용오차 기반 테스트를 설계합니다.

## 10. 완료 기준

- [ ] GUI/Headless에서 동일 씬을 생성했다.
- [ ] 시각적 요소와 물리 설정을 구분한다.
- [ ] 실제 설치 버전과 API import 결과를 기록했다.
- [ ] 단일 큐브 실행만으로 로봇 동작을 검증했다고 주장하지 않는다.

## 11. 질문과 해설

**Q. 화면을 안 그리면 GPU 없는 서버에서도 같은 프로그램이 지원되나요?**  
그렇게 결론내릴 수 없습니다. 설치판의 GPU·드라이버 요구사항을 확인해야 합니다.

**Q. VisualCuboid로 이동하면 실제 주행과 같나요?**  
아닙니다. 다음 세션에서는 일부러 기구 물리 없는 프록시를 사용해 통신부터 검증합니다.

**Q. GUI에서 작업한 씬만 저장하면 자동화가 되나요?**  
초기 설정·버전·외부 에셋·reset 절차까지 재현 가능해야 합니다.

## 다음 단계
[Session 07](sessions/07_bridge_closed_loop.md).

## 참고
[I2, I3, I4]와 확인된 보관 문서 범위: [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/07_bridge_closed_loop.md`

# Session 07 — ROS 2 Bridge·Clock·AMR 폐루프

> 난이도: 중급 / 예상 4~6시간 / GPU: 필요
> 선행: Session 03·04·06
> 코드 등급 B/C: ROS·Isaac 런타임 실행 미검증

## 1. 이번 목표와 명확한 한계

다음 흐름을 연결합니다.

```text
move_client (Adapter 대역)
  → MoveTo Action
amr_server backend=odom
  → /amr_01/cmd_vel
Isaac kinematic proxy
  → /amr_01/odom
amr_server가 실제 수신 위치로 도착 판단
  → Action Result
```

이 예제의 Isaac 객체는 **VisualCuboid 기반 운동학 프록시**입니다.
실제 바퀴·접촉·충돌 회피·마찰·브레이크는 구현하지 않았습니다.
따라서 증명되는 것은 인터페이스와 feedback 기반 완료 경로입니다.
실제 물리 AMR로 교체하는 과제는 후반에 분리합니다.

## 2. 표준 메시지로만 Isaac에 연결하는 이유

업무 Action `MoveTo`는 외부 ROS 환경에만 둡니다.
Isaac 프로세스 내부는 표준 타입만 import합니다.

| 내부 인터페이스 | 역할 |
|---|---|
| geometry_msgs/Twist | 선속도·각속도 입력 |
| nav_msgs/Odometry | 프록시 위치·속도 출력 |
| rosgraph_msgs/Clock | 학습 씬 시간 |

공식 설치 문서는 기본 타입과 사용자 정의 Python 인터페이스의 런타임 구성을 구분합니다.[I1]
이 설계는 그 경계를 단순화하는 프로젝트 선택입니다.

## 3. 실행 전 환경 점검

1. 실제 Isaac 버전을 기록합니다.
2. 그 버전 공식 ROS 설치/Standalone 문서대로 내부 라이브러리를 설정합니다.[I1, I2]
3. ROS terminal과 Isaac terminal의 Domain·RMW를 맞춥니다.
4. 외부 ROS overlay를 Isaac에 무조건 source하지 않습니다.
5. 같은 domain에서 `/clock` publisher가 하나인지 확인합니다.

`python.sh`의 자동 ROS 설정 범위는 설치 버전에 따라 다를 수 있으므로
예전 블로그의 LD_LIBRARY_PATH를 그대로 복사하지 않습니다.

## 4. 코드 해설 — 수신 콜백은 값을 저장

`kinematic_amr_bridge.py`:

```python
def command(msg):
    if math.isfinite(msg.linear.x) and math.isfinite(msg.angular.z):
        received[:] = [
            time.monotonic(),
            max(-1.0, min(1.0, msg.linear.x)),
            max(-1.0, min(1.0, msg.angular.z)),
        ]
```

값 제한은 실습 안전장치이며 실제 장비 안전 기능이 아닙니다.
나쁜 NaN 값은 받아들이지 않습니다.

simulation loop에서:
1. ROS callback 처리.
2. command freshness 검사.
3. 프록시 좌표 적분.
4. 씬 transform 적용.
5. world.step.
6. Clock과 odom 발행.

코드의 핵심:

```python
rclpy.spin_once(node, timeout_sec=0.0)
if received[0] is None or time.monotonic() - received[0] > 0.5:
    v = w = 0.0
yaw += w * period
x += v * math.cos(yaw) * period
y += v * math.sin(yaw) * period
```

0.5초는 학습용 command timeout입니다.
이는 “새 명령이 없으면 프록시 적분을 멈춘다”는 뜻이지 실제 안전 정지 인증이 아닙니다.

## 5. 실습 A — Bridge 단독 확인

[QUICKSTART](appendices/QUICKSTART.md)의 환경 준비 후:

```bash
"$ISAAC_SIM_ROOT/python.sh" \
  "$STUDY_ROOT/examples/isaac_sim/kinematic_amr_bridge.py" \
  --namespace amr_01
```

ROS 터미널에서:

```bash
ros2 topic echo /clock
ros2 topic echo /amr_01/odom
ros2 topic info /amr_01/cmd_vel --verbose
```

상자 프록시가 초기 위치에 있고 odom이 주기 발행되는지 확인합니다.
이 예제는 clock을 loop step으로 계산하며 실행 중 GUI reset/pause 재현은 지원하지 않습니다.
pause/reset 시험은 공식 timeline 연계로 확장한 뒤 실시합니다.

## 6. 실습 B — 외부 Action 서버 연결

mock 서버가 종료되었는지 확인한 뒤:

```bash
ros2 run study_nodes amr_server --ros-args \
  -r __ns:=/amr_01 -p device_id:=amr_01 \
  -p backend:=odom -p use_sim_time:=true
```

다른 터미널:

```bash
ros2 run study_nodes move_client --ros-args \
  -r __ns:=/amr_01 -p x:=1.0 -p y:=1.0 -p speed:=0.3
```

기대 조건:
- 유효한 odom을 받기 전에는 Goal이 거부됨.
- 수신 후 속도 명령이 발행됨.
- 상자와 odom 위치가 변함.
- 거리 오차 0.03m 이내에서 성공.
- 결과 후 속도 0 명령 발행.

성공 시 yaw·정지 속도·접촉은 확인하지 않는 예제임을 결과표에 적습니다.

## 7. 실습 C — 통신 단절의 양방향 관찰

**실험 1: Isaac 프로세스 종료**
- Action 서버는 odom 수신이 끊겨 STALE_POSE로 실패해야 함.
- 예제 task timeout보다 pose timeout이 먼저 발생하는지 관찰.

**실험 2: Action 서버 종료**
- 프록시 command watchdog이 마지막 명령 수신 이후 이동을 멈춰야 함.
- 실제 정지 시간은 wall time 기준으로 기록.

**주의:** 프로세스 전체 종료는 DDS packet loss의 정밀 모사가 아닙니다.
수신 지연만 재현하려면 별도 relay 노드에서 메시지를 지연/드롭하는 확장을 만듭니다.

## 8. 좌표·쿼터니언·시간 주의사항

- 예제 goal/odom은 같은 `map` 평면입니다. 서버는 TF 변환을 하지 않습니다.
- ROS Quaternion은 x/y/z/w 필드, 예제 Isaac 배열은 w/x/y/z 순서로 작성했습니다.
  설치 API가 요구하는 순서를 확인합니다.
- 값이 바뀌어도 frame이 틀리면 움직임의 의미는 틀립니다.
- odom은 추정치가 아니라 ground truth 프록시 상태입니다.
- `/clock`은 하나만 발행. 별도 프로세스로 이 Bridge를 10개 실행하면 Clock 충돌 위험이 있습니다.
- fixed step과 실시간 pacing은 같지 않습니다. 부하가 크면 실제 시간이 더 걸립니다.

## 9. 물리 AMR로 교체하는 고급 과제

**외부 계약은 유지하고 내부를 교체**합니다.

1. 물리적으로 설정된 AMR USD를 로드.
2. Twist를 차동 구동 controller로 전달.
3. wheel joint 명령 적용.
4. 실제 chassis pose/velocity를 읽어 odom 발행.
5. Scene reset과 simulation clock 연계.
6. 발행 주기·stale·취소·완료 계약 회귀 테스트.

수정 금지에 가까운 경계:
- Adapter의 MoveTo Action 계약.
- task_id 의미.
- timeout과 결과 코드 의미.

변경 가능한 내부:
- 위치 생성 방식.
- controller.
- joint와 prim 경로.
- 센서.

Nav2는 장애물 회피 결과가 Adapter 테스트의 일부일 때 선택적으로 추가합니다.
처음부터 지도·SLAM·local planner 튜닝을 학습 필수로 두지 않습니다.

## 10. 운영 체크·완료 기준

- [ ] 코드의 ROS 표준/사용자 정의 타입 경계를 이해한다.
- [ ] 실제 설치판 Bridge 환경을 기록했다.
- [ ] odom freshness 없이 목표를 수락하지 않는다.
- [ ] 양방향 프로세스 중단을 시험했다.
- [ ] “kinematic 성공”을 “물리 주행 검증 완료”로 쓰지 않는다.
- [ ] 실행 중 reset 미지원이라는 한계를 기록했다.

## 11. 질문과 해설

**Q. 타이머가 10초 지났으니 도착 처리하면 안 되나요?**  
실제 위치 피드백을 검증하려는 odom 모드에서는 안 됩니다. 경량 mock 모드와 목적이 다릅니다.

**Q. Bridge에서 직접 MoveTo Action을 제공하면 안 되나요?**  
가능한 별도 설계지만 커스텀 타입·런타임·업무 상태가 Isaac에 결합됩니다. 본 교재는 분리를 택합니다.

**Q. cmd_vel에 다른 publisher가 하나 더 있어도 괜찮나요?**  
예제에는 명령 arbitration이 없습니다. 한 장비의 제어 권한을 단일화하거나 별도 mux를 구현해야 합니다.

## 다음 단계
[Session 08](sessions/08_cobot_equipment_handover.md).

## 참고
[I1, I2, I4]: [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/08_cobot_equipment_handover.md`

# Session 08 — 협동로봇·PLC 설비·화물 인계·인터록

> 난이도: 중급 / 예상 4~6시간 (설계·순수 로직 실습)
> GPU: 기본 로직 불필요, 관절 연동 확장에는 필요
> 선행: Session 03·05, 물리 확장은 Session 07
> 구현 범위: RunProgram 스키마와 인터록/예약 순수 코드 제공.
> **협동로봇 ROS Action 서버·PLC 프로토콜 서버는 제공하지 않습니다.**

## 1. AMR와 협동로봇의 차이

AMR에는 “목적지 이동”이 주요 명령인 반면,
협동로봇 테스트는 “정의된 작업 프로그램 실행”으로 시작하는 안을 제안합니다.

예:
- `pick_from_amr`
- `place_to_conveyor`
- `return_home`

이름은 프로젝트용 제안이며 벤더의 실제 프로그램 API가 아닙니다.
실제 Adapter가 joint trajectory를 직접 주는지, 프로그램 ID만 주는지 먼저 확인해야 합니다.

## 2. 학습 Action 스키마

제공 파일: `study_interfaces/action/RunProgram.action`

```text
string task_id
string program_id
string cargo_id
uint64 cell_epoch
---
bool success
string code
---
string phase
```

서버 구현 전 결정할 사항:
- 허용 프로그램 목록.
- 이미 실행 중일 때 거부/큐잉.
- 취소 가능한 구간과 금지 구간.
- 작업 실패 시 화물 위치.
- AMR 출발을 허가하는 조건.
- 같은 program_id라도 cargo_id가 다르면 다른 업무 작업으로 취급하는 규칙.

Action을 쓰는 이유는 장시간 작업·결과·취소를 구분하려는 것입니다.[R1]

## 3. 인계 상태 머신 — 설계안

```text
AVAILABLE
  → RESERVED
  → WAIT_AMR
  → VERIFY_DOCK
  → READY_TO_TRANSFER
  → TRANSFERRING
  → VERIFY_CARGO
  → COMPLETED
```

별도 종료/복구 상태:
- FAILED
- CANCEL_PENDING
- RECOVERY_REQUIRED
- UNKNOWN

협동로봇 관절 동작이 끝났더라도 화물 인계가 확인되지 않았으면 공정 완료로 처리하지 않습니다.
그리퍼·광전센서·화물 ID 확인이 무엇을 증명하는지 각각 정의합니다.

## 4. 순수 Python 코드 — 시작 조건

`core.py`:

```python
@dataclass(frozen=True)
class Interlock:
    docked: bool
    amr_stopped: bool
    arm_ready: bool
    output_clear: bool
    communication_fresh: bool

    def ready(self):
        return all((self.docked, self.amr_stopped,
                    self.arm_ready, self.output_clear,
                    self.communication_fresh))
```

이 코드는 시작 조건의 논리 예제이며 안전 PLC를 대체하지 않습니다.
실제 동작 중 조건이 깨졌을 때의 정지·복구 정책은 별도로 필요합니다.
출력 버퍼가 막힌 상태에서도 시간만 지나면 SUCCESS가 되는 가상 설비는 좋은 대역이 아닙니다.

## 5. 실습 A — 순수 인터록 실행

루트에서 순수 테스트 환경을 활성화:

```bash
export PYTHONPATH="$PWD/examples/ros2_ws/src/study_nodes"
python examples/pure_python/cell_demo.py
```

기대:
- 준비 조건이 true면 handover permitted 출력.
- 이미 해제한 예약의 중복 해제는 거부.

**수정 과제**
1. communication_fresh를 false로 바꿈.
2. arm_ready를 false로 바꿈.
3. 어느 조건이 false인지 상세 거부 사유를 반환하는 함수를 추가.
4. 논리 조합별 단위 테스트 작성.

## 6. 예약의 epoch가 필요한 이유

예를 들어:
1. 작업 A가 셀을 예약, epoch=1.
2. A가 끝나고 예약 해제.
3. 작업 B가 같은 셀 예약, epoch=2.
4. A의 늦은 완료 메시지 도착.

owner 문자열만 보면 A/B를 구분하기 어려울 수 있습니다.
`Lease` 예제는 owner와 epoch가 둘 다 맞아야 해제를 허용합니다.

```python
epoch = lease.acquire("amr_01")
lease.release("amr_01", epoch)
```

이 예제는 **단일 프로세스** 논리입니다. 네트워크 분할·분산 consensus·재시작 영속성은 구현하지 않습니다.
같은 아이디어를 분산 시스템에 쓸 때는 epoch 발급 주체와 저장소 일관성을 설계해야 합니다.

## 7. 실습 B — ROS 협동로봇 서버 설계 과제

제공 MoveTo 서버 구조를 참고하되 아래를 새로 작성합니다.

| 콜백/상태 | 해야 할 일 |
|---|---|
| goal | program allowlist, task 중복, 인터록, epoch 검증 |
| accepted | 작업 컨텍스트 생성 |
| timer/backend | mock 시간 또는 실제 joint feedback으로 진행 |
| cancel | 현재 공정 단계의 취소 가능 여부 결정 |
| result | 성공/실패/복구 필요 상태 반환 |
| state | 현재 프로그램·cargo·step·fault 발행 |

**초기 mock 운영 규칙 제안**
- 프로그램 실행 시간은 설정값.
- 성공 전에 인터록을 다시 확인.
- 장애 주입 시 타이머만 멈추는 것이 아니라 실패 결과와 화물 상태를 남김.
- cancel을 받았다고 화물을 자동으로 원래 위치로 돌리지 않음.

완료 기준은 ROS 서버를 직접 구현한 뒤 실제 테스트로 채웁니다.
스키마가 빌드되었다고 이 과제가 완료된 것은 아닙니다.

## 8. PLC 설비의 범위 구분

본 프로젝트에서 PLC 설비를 ROS 노드로 모사할 수 있지만,
이것만으로 OPC UA/Modbus/TCP/vendor PLC 프로토콜 Adapter를 검증했다고 볼 수 없습니다.

| 테스트 대상 계약 | 필요한 대역 |
|---|---|
| ROS 2 설비 제어 인터페이스 | ROS Service/Topic/Action 서버 |
| 실제 PLC 프로토콜 | 해당 프로토콜 서버·태그/레지스터·타이밍 모사 |
| PLC 내부 sequence 자체 | 실제 로직 또는 PLC 시뮬레이터 등 별도 범위 |

사용자님의 현재 가정인 ROS 2 제어 시스템 연동에 맞춰 우선 첫 번째를 학습합니다.

## 9. Isaac 협동로봇으로 확장

구현 계획:
1. 관절 이름·초기 자세·목표 자세를 명시.
2. 외부 RunProgram에서 내부 관절 명령으로 변환.
3. Isaac 관절 feedback과 목표의 오차 확인.
4. 위치 오차가 일정 시간 유지되고 속도가 충분히 작을 때 동작 완료.
5. 화물 인계 확인 후 공정 완료.

초기에는 미리 정한 자세 sequence를 사용합니다.
MoveIt 2·충돌 회피 계획·force control은 실제 검증 목표에 필요할 때 추가하는 선택 과제입니다.
모델마다 API·joint 순서가 달라 여기서는 검증되지 않은 완성 제어 코드를 제공하지 않습니다.

## 10. 주의사항·고급·운영

- 화물 소유권을 AMR과 셀이 동시에 갖는 상태를 금지하는 invariant를 정의합니다.
- Lift 진입 허가·도어·층·점유는 별도 조건으로 유지합니다.
- Conveyor의 상류/하류 준비와 구간 점유를 분리합니다.
- AS/RS는 입출고 포트와 재고 정합성부터 시작합니다.
- 장애 중 인계 상태 UNKNOWN이면 무조건 재피킹하지 않습니다.
- 이 교재 인터록은 공정 논리이며 안전 기능으로 사용하면 안 됩니다.
- 작업 취소 불가 구간이 있으면 Adapter에 명시적으로 알려야 합니다.

## 11. 완료 기준

- [ ] RunProgram 스키마와 구현 과제를 구분한다.
- [ ] false 인터록에서 시작이 거부되는 단위 테스트를 작성했다.
- [ ] 오래된 epoch 해제가 거부되는 이유를 설명한다.
- [ ] 관절 완료와 화물 인계 완료를 구분한다.
- [ ] 실제 PLC 통신 검증의 추가 범위를 설명한다.

## 12. 질문과 해설

**Q. AMR이 목표 좌표에 있으면 협동로봇을 시작해도 되나요?**  
위치 외 정지·정렬·예약·화물·통신 freshness 조건이 필요할 수 있습니다. 공정 계약으로 정해야 합니다.

**Q. cancel 후 cargo owner를 원래 값으로 되돌리면 되나요?**  
실제 인계가 어느 단계였는지 모르므로 임의 되돌리기는 위험합니다. 확인/복구 상태가 필요합니다.

**Q. ROS 설비 노드로 PLC Adapter 테스트를 끝낼 수 있나요?**  
Adapter의 실제 외부 계약이 ROS라면 해당 범위를 검증할 수 있습니다. PLC 프로토콜 자체는 별도입니다.

## 다음 단계
[Session 09](sessions/09_test_automation_metrics.md).

## 참고
[R1] 및 본 교재 설계. [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/09_test_automation_metrics.md`

# Session 09 — 자동 검증·로그·rosbag·성능 측정

> 난이도: 중급 / 예상 3~5시간 / GPU: 기능 범위에 따라 선택
> 선행: Session 03·05, 물리 테스트는 Session 07

## 1. 실행 성공과 테스트 성공의 차이

프로세스가 오류 없이 끝났다고 Adapter가 올바른 것은 아닙니다.
입력, 예상 결과, 실제 결과, 제한 시간, 검증 근거가 있어야 테스트입니다.

본 세션의 목표:
- 순수 로직 → ROS 계약 → Isaac 통합의 테스트 층 분리.
- 실패·거부·UNKNOWN도 보고서에 포함.
- 접수 지연과 작업 수행 시간을 분리.
- 측정 조건이 다른 결과를 같은 성능 숫자로 비교하지 않기.

## 2. 테스트 계층

| 계층 | 실행 환경 | 예 |
|---|---|---|
| 순수 단위 | Python만 | 중복·취소·timeout·lease |
| ROS 계약 | ROS, GPU 없음 | Action 수락/결과/취소 |
| 경량 다중 장비 | ROS, GPU 없음 | 10대 동시 작업·단일 고장 |
| Isaac 통합 | GPU | 위치 기반 완료·pose stale |
| 외부 Adapter E2E | 사용자 시스템 포함 | 명령/상태 변환·재연결 |

이번 작성 환경에서 실제 수행한 것은 첫 번째와 Python 문법 검사입니다.
나머지 통과 여부는 사용자의 환경에서 기록합니다.

## 3. 실습 A — 단위 테스트

```bash
bash scripts/check_local.sh
```

예제 테스트를 읽습니다.

```python
def test_timeout_wins_same_tick():
    m = Motion()
    m.start(Request("a", 1, 0, speed=1, timeout_sec=1))
    m.tick(1)
    assert m.detail == "TIMEOUT"
```

핵심은 “코드가 이 결과를 냈다”가 아니라 “동일 tick이면 timeout 우선이라는 계약”을 고정하는 것입니다.
정책을 바꾸면 테스트도 의식적으로 변경하고 리뷰합니다.

**추가 과제**
- tolerance 경계.
- 음수·NaN 입력.
- 기존 task 완료 직후 신규 Goal.
- cancel과 fault가 동시에 관측될 때.
- ledger full 후 기존 결과 조회 정책.
- boot_id가 바뀐 상태에 대한 Adapter 반응.

## 4. 실습 B — 로그를 남기는 정상 client

먼저 AMR 서버가 실행 중이어야 합니다.

```bash
mkdir -p artifacts/session09
ros2 run study_nodes move_client --ros-args \
  -r __ns:=/amr_01 -p x:=1.0 \
  -p output:="$PWD/artifacts/session09/client.jsonl"
```

같은 장비에 반복 작업하려면 x:=0.0과 x:=1.0을 번갈아 사용합니다.
항상 같은 도착점만 주면 이후 요청은 거의 이동하지 않으므로 이동 성능을 비교할 수 없습니다.

JSONL 필드:
- accept_latency_ms: 요청 송신 직전부터 수락 응답을 처리한 때까지.
- completion_ms: 요청 시작부터 결과를 처리한 때까지.
- status/code/success.
- cancel 요청 여부.

**중요한 한계:** 제공 client는 정상 수락·종료 레코드만 파일에 씁니다.
거부·접수 UNKNOWN·결과 UNKNOWN은 예외로 출력하므로, 이 파일만으로 전체 실패율을 계산하면 편향됩니다.
실제 부하 실행기는 모든 시도에 start/end/exit_code/unknown을 반드시 기록하도록 확장하십시오.

## 5. 실습 C — 지표 집계

```bash
python examples/pure_python/summarize.py artifacts/session09/client.jsonl
```

집계 코드는 nearest-rank 방식의 percentile을 사용합니다.

```python
values = sorted(values)
index = max(0, math.ceil(p / 100 * len(values)) - 1)
return values[index]
```

이 정의를 보고서에 명시합니다.
소수 표본의 p99는 거의 최대값이므로 시스템 전체 지연 보장이라고 해석하지 않습니다.
제공 테스트용 숫자는 측정 실적이 아닌 계산 검증 입력입니다.

## 6. 부하 시나리오 설계

**계획 예시이며 공식 성능 기준이 아닙니다.**

1. warm-up 1회.
2. AMR 1대, 3대, 10대별 동일한 task 분포.
3. 각 장비에 동시에 최대 1개 활성 작업.
4. 정상 종료 후 다음 작업.
5. 별도 burst 시험에서는 BUSY 거부를 기대 결과로 분류.
6. 이상치 포함 raw samples 보존.
7. mock과 Isaac 결과를 다른 표로 보고.

처리량 분모:
- accepted tasks / sec
- completed tasks / sec
- attempted tasks / sec

모두 같은 값이 아닙니다.
백로그를 늘려 접수량만 높이는 것을 처리 성능 개선으로 발표하지 않습니다.

## 7. rosbag 활용 과제

ROS 설치판에서 `ros2 bag --help`와 사용 가능한 storage plugin을 먼저 확인합니다.

예시 명령 (로컬 검증 필요):

```bash
ros2 bag record -o artifacts/session09/bag \
  /amr_01/state /amr_01/cmd_vel /amr_01/odom /clock
```

주의:
- 이 명령은 위 Topic을 기록하는 예시이지 모든 Action request/response를 기록하는 명령이 아닙니다.
- 외부 계약용 이벤트 로그를 별도로 유지합니다.
- playback은 업무 로직의 결정적 재실행이나 영구 상태 복구를 자동 보장하지 않습니다.
- 실제 장비망에서 command Topic을 재생하지 마십시오.
- QoS·시계·백엔드 상태가 원래 실행과 다르면 결과가 달라질 수 있습니다.

Jazzy의 해당 공식 문서는 이번 도구 조회에서 접근 제한이 있어, 설치판 문서 확인을 별도 과제로 남깁니다.

## 8. 장애 주입의 층

| 장애 | 간단한 재현 | 검증 범위 |
|---|---|---|
| 장비 실패 | test/set_fault | 업무 실패 매핑 |
| 상태 중단 | 서버 종료 | freshness·재시작 |
| 결과 미수신 | client 통신 차단/별도 relay | UNKNOWN 처리 |
| 명령 지연 | relay의 delayed delivery | timeout·늦은 명령 |
| 네트워크 손실 | 격리 시험망의 네트워크 에뮬레이션 | 실제 transport 영향 |
| 씬 정지 | timeline 연동 구현 후 pause | clock/timeout 정책 |

파괴적인 `tc`/방화벽 변경 명령은 공유 서버에 그대로 적용하지 않습니다.
별도 시험 환경과 복구 명령을 준비한 후 수행합니다.

## 9. 결과 보고서 양식

```text
run_id:
git_commit:
contract_version:
backend:
os/ros/isaac/driver:
device_counts:
scenario_id:
seed:
sensor/render_profile:
warmup:
attempts / accepted / succeeded / failed / rejected / unknown:
accept_latency_ms: n, p50, p95, p99, max
task_completion_ms: n, p50, p95, p99, max
sim_delta_sec / wall_delta_sec:
max_vram:
failure_evidence:
limitations:
```

RTF는 같은 구간의 `sim_delta / wall_delta`로 계산합니다.
초기 로딩 시간과 steady-state 구간을 분리하십시오.
같은 host에서 측정한 monotonic 값으로 client 왕복 지연을 계산하면 호스트 간 시각 동기화 오차를 피할 수 있습니다.

## 10. 고급·운영 고려사항

- 측정 client가 결과를 소비하지 못해 병목이 되는지도 확인합니다.
- p99를 줄이기 위해 오류 요청을 제외하면 보고서가 왜곡됩니다.
- 로그 기록 자체의 CPU·디스크 비용을 측정합니다.
- pytest/launch_testing 기반 자동 계약 테스트는 다음 확장입니다.
  이번 패키지에 launch_testing E2E suite가 이미 구현되어 있는 것은 아닙니다.
- 실제 Adapter를 시험할 때는 이 교재 client를 해당 Adapter로 교체합니다.
- 시뮬레이터 성능과 Adapter 성능을 분리하려면 별도 host 또는 자원 제한 시험을 비교합니다.

## 11. 완료 기준

- [ ] 단위 테스트를 직접 실행하고 결과를 저장했다.
- [ ] 실제 client JSONL을 수집·집계했다.
- [ ] 집계에 포함되지 않은 요청을 명확히 적었다.
- [ ] 접수 지연과 완료 시간을 혼동하지 않는다.
- [ ] 정상·거부·실패·UNKNOWN을 분류한 보고서 초안을 작성했다.

## 12. 질문과 해설

**Q. p99가 20ms면 모든 요청이 20ms 이내인가요?**  
아닙니다. 표본의 정의와 percentile 방식, 제외된 실패를 함께 봐야 합니다.

**Q. rosbag만 있으면 실패가 완전히 재현되나요?**  
그렇게 보장할 수 없습니다. 업무 상태·동시성·시뮬레이션 조건이 추가로 필요합니다.

**Q. mock 결과와 Isaac 결과를 같은 그래프로 비교해도 되나요?**  
가능하지만 서로 다른 workload임을 명확히 표시해야 합니다. 차이를 Adapter 성능 변화로 곧바로 해석하면 안 됩니다.

## 다음 단계
[Session 10](sessions/10_advanced_operations_capstone.md).

## 참고
본 세션 지표와 절차는 프로젝트 설계입니다.
ROS 문서 확인 범위: [SOURCES](appendices/SOURCES.md).



---

원본: `sessions/10_advanced_operations_capstone.md`

# Session 10 — 고급 기술·운영 전환·AMR 10대 + 협동로봇 5대

> 난이도: 중급~고급 / 예상 6~10시간 (설계·계획 작성)
> 실제 15대 통합 구현은 별도 일정 필요
> 선행: Session 00~09

## 1. 최종 목표

이 세션은 완성된 15대 시스템을 실행하는 자동 스크립트가 아닙니다.
제공된 AMR 학습 코드를 바탕으로 사용자님의 실제 Adapter 검증 환경으로 확장하는 계획을 만듭니다.

최종 공정 예:
**출고 요청 → AMR 할당 → 버퍼 도착 → 셀 예약 → 협동로봇 인계 → Conveyor 배출 → 완료**

평가 대상:
- 장비별 명령 계약.
- 병렬 작업 간 상태 격리.
- 물류 인계의 정합성.
- 장애 후 작업 복구.
- 로그로 결과를 설명할 수 있는가.

## 2. 코드 예제의 현재 위치

| 항목 | 제공 상태 | 다음 개발 |
|---|---|---|
| AMR mock 1~10대 | 코드 제공, ROS 실행 미검증 | 실제 ROS 회귀 검증 |
| AMR Isaac 프록시 1대 | 코드 제공, Isaac 실행 미검증 | 물리 모델·다중 배치 |
| 협동로봇 5대 | 스키마/설계만 | 서버·joint backend |
| PLC 설비 | 인터록/설계만 | 설비 state machine/프로토콜 |
| 영구 작업 저장 | 없음 | 이력 조회·멱등성 |
| reset orchestration | 없음 | quiesce/reset/reconcile |
| 자동 E2E 판정기 | 일부 순수 테스트만 | ROS/Adapter/GPU suite |
| 운영 보안 | 체크리스트 | 접근 제어·격리·감사 |

이 표를 이해한 상태에서 범위를 산정합니다.

## 3. 최소 운영 아키텍처 제안

```text
외부 Adapter들
  ├── AMR ROS 계약
  ├── Cobot ROS 계약
  └── 설비 ROS 계약
          |
가상 장비 상태 머신 (장비별)
          |
공통 backend 계약
  ├── 경량 동작 / 장애 주입
  └── Isaac scene manager
          |
Clock·에셋·prim·joint·센서
```

교차 관심사:
- run coordinator.
- immutable run config.
- event log / result ledger.
- health / metrics.
- scenario runner / oracle.

업무 상태는 ROS 가상 장비, 물리 상태는 시뮬레이터에서 관리하되
화물 소유권과 공정 완료의 **최종 결정 주체**를 명시합니다.
같은 값을 여러 서버가 독립적으로 수정하는 구조를 피합니다.

## 4. 고급 기술: 우선순위

| 우선순위 | 기술 | 도입 조건 |
|---|---|---|
| 필수 | 지속 작업 이력·재연결 정합성 | Adapter 재시도/복구 검증 |
| 필수 | run_id·epoch·준비 상태 | 반복 실행·reset |
| 권장 | pytest 기반 계약 자동화 | 변경 회귀 방지 |
| 권장 | ROS 실행 자동 테스트 도구 | 노드 기동·종료·endpoint 테스트 |
| 권장 | tf2·프레임 검증 | 복수 프레임/실제 로봇 도입 |
| 선택 | Nav2 | 장애물 회피/경로 결과가 테스트 범위 |
| 선택 | MoveIt 2 | joint 명령보다 복잡한 계획이 필요한 경우 |
| 선택 | C++ 노드·프로세스 분리 | Python/콜백 병목이 실측된 경우 |
| 선택 | DDS 발견 서버·보안 구성 | 네트워크 규모/보안 요구 |
| 선택 | Isaac ROS·인식 가속 | 센서 인식 검증이 목표에 포함될 때 |

이 목록은 기능 소개가 아닌 도입 조건입니다.
패키지 버전과 호환 조합은 실제 도입 단계에 공식 문서로 다시 확인합니다.
선택 기술을 모두 먼저 설치하는 것을 학습 목표로 삼지 않습니다.

## 5. reset의 올바른 순서

설계 예:

1. 신규 작업 수락 중지.
2. 진행 작업 목록 snapshot.
3. 취소/중단 요청.
4. 정지·이관 상태 확인.
5. 기존 작업을 terminal 또는 UNKNOWN으로 기록.
6. ROS backend 연결 분리.
7. 씬 위치·화물·점유 초기화.
8. 새 run_id/epoch 발급.
9. clock/pose/장비 readiness 확인.
10. 외부 Adapter에 새 실행 경계 통지 후 재개.

오래된 완료 응답이 새 실행의 작업을 끝내지 못해야 합니다.

### 짧은 검증 예제

```python
expected_epoch = 8
incoming_event = {"task_id": "T-1", "epoch": 7, "phase": "SUCCEEDED"}
if incoming_event["epoch"] != expected_epoch:
    decision = "IGNORE_STALE_EVENT"
else:
    decision = "APPLY"
assert decision == "IGNORE_STALE_EVENT"
```

이 코드는 epoch 비교 원리만 보여줍니다.
실제 분산 저장소·원자성·인증이 구현된 것은 아닙니다.

## 6. 영구 멱등 처리 설계

저장 키:
- device_id
- task_id
- request_hash
- accepted_at
- phase
- backend_execution_id
- result
- boot_id / run_id

중요한 장애 창:
- 저장 성공, 실행 전 crash.
- 실행 시작, 상태 저장 전 crash.
- 실행 완료, 결과 응답 전 crash.

“DB에 UNIQUE를 걸면 exactly-once가 완성된다”로 단순화하지 않습니다.
외부 동작과 저장 트랜잭션이 같은 원자 단위가 아닐 수 있으므로,
실행 상태 조회·재조정·업무 보상 절차를 설계합니다.

예제 메모리 ledger는 이 요구를 충족하지 않습니다.

## 7. 보안·실제 운영 고려사항

- 학습 노드를 실제 AMR/협동로봇의 cmd_vel/joint endpoint와 같은 domain/network에 연결하지 않습니다.
- Domain ID 외에도 네트워크·방화벽·인증 정책이 필요합니다.
- test/set_fault는 테스트 제어 plane에 한정합니다.
- CPU/GPU memory, 큐 길이, 디스크 용량 상한을 둡니다.
- 로그에 인증 정보나 실제 생산 주문의 민감 데이터를 그대로 남기지 않습니다.
- 외부 에셋의 배포 권한·다운로드 자격증명을 관리합니다.
- crash 자동 재기동은 health 회복이지 작업 정합성 회복이 아닙니다.
- 변경마다 문서/계약/테스트/버전 기록을 함께 갱신합니다.

운영 상세: [OPERATIONS_CHECKLIST](appendices/OPERATIONS_CHECKLIST.md).

## 8. 단계별 최종 프로젝트

### Gate A — ROS 경량 단일 장비
- 성공·취소·거부·실패·UNKNOWN 정의.
- 동일 ID 재시도 정책.
- wall/sim time 정책.
- Action 결과와 Adapter 상태 매핑표.

### Gate B — AMR 다중 장비
- 10대 동시 endpoint와 고장 격리.
- 잘못된 device_id 검출.
- 재시작 이후 boot_id 변화 처리.
- mock 처리량/지연 보고.

### Gate C — Isaac AMR
- 프록시→물리 로봇 교체.
- 이동·정지 feedback.
- Scene stop/reset 경계.
- GPU/VRAM/RTF 측정.

### Gate D — 협동로봇·설비
- RunProgram 서버 구현.
- 시작/완료 인터록.
- 화물 중복 소유 금지.
- 버퍼 full, lift occupied, conveyor jam.

### Gate E — 10대+5대 통합
- 여러 AMR이 5개 셀 공유.
- 공용 구간 예약 및 셀 경합.
- 한 셀 고장 시 나머지 영향 범위.
- 진행 작업 복구와 인계 UNKNOWN 처리.
- 실제 Adapter를 연결해 E2E 결과 수집.

## 9. 최종 합격표 제안

아래 수치들은 프로젝트에서 합의하여 채웁니다. 임의로 제품 보장치를 만들어 넣지 않습니다.

| 영역 | 지표 | 합격 기준 |
|---|---|---|
| 계약 | 잘못된 상태 매핑 | 허용 여부/건수 합의 |
| 정합성 | 화물 중복 소유 | 금지 invariant |
| 복구 | UNKNOWN 해소 | 허용 절차·시간 합의 |
| 성능 | 접수 p95/p99 | 실제 workload 기준 합의 |
| 공정 | 처리량·대기·병목 | 시나리오 기준 합의 |
| 시뮬레이션 | RTF·pose freshness | 목표 실시간성에 맞춰 합의 |
| 리소스 | VRAM·큐·디스크 | 측정 장비 기준 상한 |
| 재현성 | 버전/설정 누락 | 실행마다 추적 가능 |

기술 데모의 “보기에 부드러움”을 성능 합격 기준으로 삼지 않습니다.

## 10. 최종 제출물

- architecture.md
- interface_contract.md
- environment_manifest.yaml
- scenarios/*.yaml
- logs와 raw samples
- 정상/장애/복구 결과 보고서
- known_limitations.md
- 운영 체크리스트
- 다음 개발 backlog

**학습 완료와 운영 완료는 다릅니다.** 모르는 항목을 한계로 적고 다음 검증 계획을 세우는 것도 중요한 결과입니다.

## 11. 확인 질문과 해설

**Q. 15대를 실행하면 대규모 성능 검증이 끝나나요?**  
아닙니다. 동시 요청 분포·센서·공정 복잡도·고장·장시간 실행·리소스가 함께 정의되어야 합니다.

**Q. 로봇 위치는 Isaac, 작업 완료는 타이머로 두면 되나요?**  
물리 결과를 검증하려는 모드에서는 실제 상태를 완료 조건에 연결해야 합니다. 타이머는 timeout이나 mock용입니다.

**Q. Python을 C++로 모두 바꾸면 운영성이 해결되나요?**  
언어 변경만으로 계약·멱등성·복구·보안은 해결되지 않습니다. 측정된 병목이 있는 경로부터 전환합니다.

## 최종 권장 순서

**ROS 경량 계약 → 1대 Isaac 폐루프 → 협동로봇·설비 인계 → 10대+5대 확장 → 운영 복구** 순서로 진행하십시오.

## 참고
본 세션은 사용자 목표에 맞춘 설계 제안입니다.
선택 기술은 도입 전에 설치 버전 공식 문서를 재확인합니다.
[I1, I2, I3]의 기반 문서: [SOURCES](appendices/SOURCES.md).



---

원본: `appendices/QUICKSTART.md`

# 빠른 실행: 각 명령의 환경을 혼동하지 않기

## 0. 작업 위치

모든 명령은 압축 해제한 `ros2_isaac_sim_study/` 루트 기준입니다.
Linux Bash 실습을 가정합니다. 실제 로봇망과 분리하십시오.

```bash
export STUDY_ROOT="$(pwd)"
```

## 1. ROS/GPU 없이 순수 Python 테스트

운영체제 Python을 오염시키지 않도록 **순수 테스트 전용** 가상환경을 사용합니다.
이 가상환경을 ROS 노드나 Isaac 실행에 그대로 쓰지 않습니다.

```bash
python3 -m venv .venv-study
source .venv-study/bin/activate
python -m pip install -r requirements-study.txt
bash scripts/check_local.sh
export PYTHONPATH="$STUDY_ROOT/examples/ros2_ws/src/study_nodes"
python examples/pure_python/cell_demo.py
deactivate
```

예상: 순수 테스트가 통과하며 `duplicate release rejected`가 출력됩니다.
작성 환경에서는 27개 통과. 로컬 결과는 새로 기록합니다.

## 2. ROS 2 패키지 빌드

전제: Ubuntu 24.04에 ROS 2 Jazzy와 colcon, rosdep 설치가 완료되어 있어야 합니다.
설치 자체는 세션 00과 공식 문서를 참고합니다. `sudo rosdep init`은 시스템당 초기 1회 절차이며 여기서 반복하지 않습니다.

새 Bash 터미널:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd "$STUDY_ROOT/examples/ros2_ws"
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --symlink-install
source install/setup.bash
ros2 interface show study_interfaces/action/MoveTo
```

각 새 터미널에서 `STUDY_ROOT`를 실제 경로로 다시 지정하거나 직접 `cd`하십시오.
환경 변수는 다른 터미널에 자동 복사되지 않습니다.

## 3. 경량 AMR 1대

터미널 A (위 ROS 환경과 workspace를 source):

```bash
ros2 run study_nodes amr_server --ros-args \
  -r __ns:=/amr_01 -p device_id:=amr_01 -p backend:=mock
```

터미널 B (동일 source / Domain / RMW):

```bash
ros2 run study_nodes move_client --ros-args \
  -r __ns:=/amr_01 -p x:=1.0 -p y:=0.0
```

터미널 C:

```bash
ros2 run study_nodes state_watch --ros-args -r __ns:=/amr_01
```

예상 결과 조건: client JSON의 `success=true`, `code=ARRIVED`.
처리 시간의 정확한 숫자는 환경 의존이며 미리 정답으로 고정하지 않습니다.

## 4. 취소·장애

기존 작업과 겹치지 않게 순차 실행합니다.

```bash
ros2 run study_nodes move_client --ros-args \
  -r __ns:=/amr_01 -p x:=5.0 -p cancel_after_sec:=0.5
```

예상: 종료 결과 `CANCEL_REQUESTED`, Action terminal status CANCELED.
CLI 프로세스를 Ctrl+C 하는 것만으로 작업 취소 성공을 판정하지 않습니다.

서버의 테스트 장애 플래그:

```bash
ros2 service call /amr_01/test/set_fault std_srvs/srv/SetBool "{data: true}"
ros2 service call /amr_01/test/set_fault std_srvs/srv/SetBool "{data: false}"
```

작업 중 true를 넣으면 실패 처리, idle에서 true를 넣으면 신규 작업 거부.
false는 플래그 해제이며 실패 작업의 자동 재실행이 아닙니다.

## 5. AMR 10대

기존 1대 서버를 먼저 종료합니다. 중복 서버를 띄우지 마십시오.

```bash
ros2 launch study_nodes fleet.launch.py count:=10
```

이 Launch는 **mock AMR만** 생성합니다. 협동로봇과 Isaac 씬은 자동 생성하지 않습니다.

## 6. Isaac 씬

ROS 전용 venv/overlay를 무심코 상속하지 않은 별도 터미널을 사용합니다.
`ISAAC_SIM_ROOT`는 `python.sh`가 실제 존재하는 설치 디렉터리입니다.
pip 설치판에는 이 경로가 없을 수 있으므로 해당 설치판 공식 실행 방식으로 바꿉니다.

```bash
export ISAAC_SIM_ROOT=/absolute/path/to/isaac-sim
"$ISAAC_SIM_ROOT/python.sh" "$STUDY_ROOT/examples/isaac_sim/scene_smoke.py"
```

이 예제는 Core API 호환성을 설치 버전에서 확인해야 합니다. GPU에서 실행 검증되지 않았습니다.

## 7. Isaac 폐루프 예제

세션 07을 읽은 뒤 진행합니다. 설치 버전에 맞는 내부 ROS 라이브러리 설정을
공식 ROS 설치 문서에서 완료해야 합니다.[I1, I2]

Isaac 터미널:

```bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
"$ISAAC_SIM_ROOT/python.sh" \
  "$STUDY_ROOT/examples/isaac_sim/kinematic_amr_bridge.py" \
  --namespace amr_01
```

ROS 터미널: 기존 mock 서버 종료 후

```bash
ros2 run study_nodes amr_server --ros-args \
  -r __ns:=/amr_01 -p device_id:=amr_01 \
  -p backend:=odom -p use_sim_time:=true
```

그 다음 일반 `move_client`로 목표를 전송합니다.
이 Bridge는 **충돌 없는 상자 프록시**이며 실제 바퀴/충돌/안전 기능을 재현하지 않습니다.

## 문서

출처 번호: [SOURCES](appendices/SOURCES.md).



---

원본: `appendices/INTERFACE_CONTRACT.md`

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



---

원본: `appendices/OPERATIONS_CHECKLIST.md`

# 운영 전환 체크리스트 — 학습 예제와 운영 코드의 차이

## 1. 격리·보안
- [ ] 실제 로봇과 연결되지 않은 NIC/네트워크/방화벽 정책
- [ ] Domain ID 외 별도 접근 제어·인증·암호화 검토
- [ ] 테스트 장애 API가 운영망에서 호출되지 않도록 분리
- [ ] 셸·컨테이너의 DDS 환경 설정을 기록
- [ ] 제3자 에셋 라이선스 확인, 접근 토큰을 Git에서 제외

## 2. 계약·정합성
- [ ] task_id/goal_uuid/device_id/boot_id/run_id 관계 정의
- [ ] 재시작 후 작업 이력 조회·멱등 처리
- [ ] Action 거부 사유 조회 방법
- [ ] 취소 수락과 실제 정지 확인 분리
- [ ] 결과 유실 시 UNKNOWN 해소 절차
- [ ] 화물 소유권·버퍼 점유의 단일 authoritative state
- [ ] 오래된 epoch의 완료 메시지 폐기
- [ ] frame·단위·쿼터니언 순서 명시

## 3. 실패 안전·리소스
- [ ] command watchdog 위치와 정지 확인
- [ ] pose stale와 프로세스 죽음의 구분
- [ ] 큐 상한·backpressure·정책별 drop/reject
- [ ] 로그 디스크 상한·순환 보관
- [ ] 핵심 상태 저장 트랜잭션 및 장애 복구
- [ ] simulation reset 이후 old task/old response 차단
- [ ] 신호 종료 후 새 명령 거부, 진행 작업 종료 정책

## 4. 실행 재현
- [ ] OS/ROS/Isaac/드라이버/에셋 버전 고정
- [ ] 환경 매니페스트와 Git commit 기록
- [ ] 코드 변경과 성능 비교 시 모델·센서·RTF 동일 조건
- [ ] 난수 seed 기록 (물리의 bitwise 동일성을 보증하지 않음)
- [ ] 상태 머신 테스트, 계약 테스트, GPU 테스트 분리
- [ ] 실제 벤더 로그·명세와 비교한 oracle 유지

## 5. 성능
- [ ] CPU 프로파일과 GPU/VRAM/RTF 동시 기록
- [ ] 수락 latency와 이동 완료 duration을 구분
- [ ] 수락/거부/UNKNOWN을 모두 분모에 포함
- [ ] 워밍업·표본 수·동시 요청 수 명시
- [ ] Adapter와 시뮬레이터 동거로 인한 자원 경합 측정
- [ ] p99 단독 수치 대신 raw samples·분포·오류율 보존

## 완료 정의

체크리스트를 채웠다는 사실만으로 안전 인증이나 실설비 검증이 완료되지는 않습니다.
실제 장비 통합은 별도 위험 평가·벤더 승인·현장 절차로 진행해야 합니다.



---

원본: `appendices/VALIDATION.md`

# 작성 자료 검증 상태

문서 기준일: 2026-09-21 KST.
다음은 실제 작성 환경에서 수행한 검사입니다. 사용자의 서버를 테스트한 결과가 아닙니다.

## 실제 실행

- Python interpreter: `3.13.5`
- 순수 Python pytest: **27 passed**
- Python AST 문법 검사: **14개 파일**
- package.xml XML 파싱: **2개 파일**
- Bash 문법 검사: **1개 파일**
- 인터록/예약 데모 실행: 통과

pytest 출력:

```text
...........................                                              [100%]
27 passed in 0.05s
```

데모 출력:

```text
handover permitted; owner=amr_01, epoch=1
duplicate release rejected: STALE_OWNER
```

## 검증한 순수 로직

- 이동 완료, 취소 후 위치 유지, 실패 상태 유지.
- BUSY 거부, 중복 ID 거부, 입력 범위/NaN/무한대 거부.
- timeout 우선순위, 외부 관측 위치 모드.
- soft reset 조건, ledger full fail-closed.
- 인터록, 예약 중복, 오래된 epoch 해제 거부.
- nearest-rank percentile과 빈 입력 검증.

## 수행하지 않은 검사

- ROS 2 / colcon 빌드·실행.
- rclpy Action 수명주기 및 DDS 통신.
- 실제 Action 취소와 동시 Goal 경합.
- Isaac Sim import/API/GPU/물리 실행.
- Nav2/MoveIt 연동.
- 물리 AMR·협동로봇 모델.
- AMR 10대+협동로봇 5대 통합 실측.
- 실제 Adapter E2E 및 실제 PLC 프로토콜.

AST 검사는 import 존재와 라이브러리 API 유효성을 검증하지 않습니다.
XML 파싱은 ROS manifest의 의미 검증이나 빌드 성공을 의미하지 않습니다.

## 환경 확인

작성 환경에서 `rclpy`, `isaacsim`, `colcon`을 사용할 수 없었습니다.
따라서 본 교재는 검증 등급 A/B/C/D를 구분합니다.

## 로컬에서 추가할 증거

1. 실제 환경 매니페스트.
2. colcon build 출력.
3. 단일 AMR 성공·취소·실패 transcript.
4. QoS/clock/odom 관찰 결과.
5. Isaac 실행 로그·최종 pose·RTF.
6. 다중 장비 및 Adapter 테스트 보고서.

실패하면 예제 자체의 문제, 설치 버전 차이, 환경 설정 문제를 구분해 수정하고
수정한 Git commit과 재검증 결과를 함께 남기십시오.



---

원본: `appendices/SOURCES.md`

# 공식 자료·버전·확인 범위

문서 확인 기준: 2026-09-21 KST. 아래 URL의 `latest`는 향후 변경될 수 있습니다.
단순 링크 나열이 아니라, 각 세션에서 근거를 사용하는 범위를 표시했습니다.
배포판이 다른 개념 문서는 개념 설명만 참고하며 Jazzy API 호환성을 검증한 것으로 해석하지 않습니다.

## ROS 2

- **[R1] Topic / Service / Action 개념 — 공식 Kilted 개념 문서 확인**
  https://docs.ros.org/en/ros2_documentation/kilted/How-To-Guides/Topics-Services-Actions.html
  사용 범위: 스트림, 짧은 RPC, 장시간 취소 가능한 작업의 역할 구분.
- **[R2] Jazzy Python Action 공식 패키지 페이지 확인**
  https://docs.ros.org/en/jazzy/p/action_tutorials_py/index.html
  사용 범위: Action 서버/클라이언트 API 학습 진입점. 본 코드 전체의 실행 보증 자료가 아님.
- **[R3] Callback Groups — 공식 Kilted 문서 확인**
  https://docs.ros.org/en/ros2_documentation/kilted/How-To-Guides/Using-callback-groups.html
  사용 범위: 상호배제/재진입 그룹, 실행기와 교착. Jazzy에서는 설치된 API로 추가 확인.
- **[R4] QoS — 공식 Humble 개념 문서 검색 결과 확인**
  https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html
  사용 범위: QoS 호환성 개념. Jazzy 실습의 상세 값은 실제 endpoint에서 확인.
- **[R5] Jazzy Service Python 공식 문서 검색 결과 확인**
  https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html
  사용 범위: 비동기 요청, 콜백 내부 spin_until_future_complete 회피.
- **[R6] 공식 Python Action 예제의 역사적 설명 확인**
  https://docs.ros.org/en/dashing/Tutorials/Actions/Writing-a-Py-Action-Server-Client.html
  Dashing은 지원 종료 배포판. 설치/런타임 기준으로 사용하지 않음.
  사용 범위: GoalHandle·Feedback·Result의 개념만 교차 확인.

### 학습자가 추가 확인할 Jazzy 원문 (이번 조회에서 접근 차단)

다음 페이지는 도구 조회가 Access Denied였으므로 본문을 확인했다고 주장하지 않습니다.
브라우저에서 접근되면 설치 버전 기준으로 API를 확인하십시오.

- https://docs.ros.org/en/jazzy/How-To-Guides/Topics-Services-Actions.html
- https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html
- https://docs.ros.org/en/jazzy/How-To-Guides/Using-callback-groups.html
- https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html
- https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html
- https://docs.ros.org/en/jazzy/p/rclpy/rclpy.action.server.html
- https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html

## Isaac Sim

- **[I0] 5.1 Standalone 문서와 지원 종료 배너 확인**
  https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ros2_tutorials/tutorial_ros2_python.html
  사용 범위: 5.1을 최신·지원 버전으로 추천하지 않는 이유.
- **[I1] 현재 ROS 2 설치 구성 안내**
  https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html
  사용 범위: Ubuntu 24.04/Jazzy 경로, 표준/사용자 정의 인터페이스,
  Isaac 런타임 Python과 외부 ROS 환경의 구분.
- **[I2] 현재 Standalone ROS 2 Bridge 문서**
  https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/bridge_configuration/tutorial_ros2_python.html
  사용 범위: SimulationApp 기반 워크플로·Bridge·Clock·manual stepping.
- **[I3] 현재 성능 최적화 안내**
  https://docs.isaacsim.omniverse.nvidia.com/latest/reference_material/sim_performance_optimization_handbook.html
  사용 범위: 렌더링·물리 비용을 구분하여 최적화하는 접근.
- **[I4] Core API Hello World, 5.1 보관 문서**
  https://docs.isaacsim.omniverse.nvidia.com/5.1.0/core_api_tutorials/tutorial_core_hello_world.html
  사용 범위: World/큐브/시뮬레이션 단계의 기본 구조.
  예제의 최신 API 실행 여부는 확인하지 않았습니다. 설치 버전에서 import 경로를 확인합니다.
- **[I5] 현재 설치 진입점**
  https://docs.isaacsim.omniverse.nvidia.com/latest/installation/quick-install.html
  다운로드·설치 경로 확인용. 교재가 특정 신규 릴리스의 안정성을 보증하지 않습니다.

## 해석 주의

- 교재의 0.05s 주기, 1s watchdog, 0.03m 도착 판정은 **학습용 설정값**입니다.
- 성능 수치·학습 시간·권장 아키텍처는 제품의 공식 보증 수치가 아닙니다.
- 출처 코드의 장문 복제 대신 독립된 학습 코드를 구성했습니다.
- 문서 링크의 버전과 실제 설치 버전을 환경 매니페스트에 함께 기록합니다.
