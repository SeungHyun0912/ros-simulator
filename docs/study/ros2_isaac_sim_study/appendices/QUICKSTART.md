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

출처 번호: [SOURCES](SOURCES.md).
