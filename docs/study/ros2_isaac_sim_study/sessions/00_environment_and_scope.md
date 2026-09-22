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

[ENVIRONMENT_MANIFEST.yaml](../appendices/ENVIRONMENT_MANIFEST.yaml)을 복사하여 관측값을 채웁니다.

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
[Session 01](01_ros_graph_workspace.md)에서 실제 ROS 패키지를 빌드합니다.

## 참고
[I0, I1]의 원문과 확인 범위: [SOURCES](../appendices/SOURCES.md).
