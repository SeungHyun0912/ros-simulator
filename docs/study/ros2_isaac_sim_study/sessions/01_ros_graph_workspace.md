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
[Session 02](02_topics_services_state.md).

## 참고
[R1, R2] 및 Jazzy 인터페이스 문서 접근 상태: [SOURCES](../appendices/SOURCES.md).
