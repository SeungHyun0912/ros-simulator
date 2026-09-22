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
[Session 07](07_bridge_closed_loop.md).

## 참고
[I2, I3, I4]와 확인된 보관 문서 범위: [SOURCES](../appendices/SOURCES.md).
