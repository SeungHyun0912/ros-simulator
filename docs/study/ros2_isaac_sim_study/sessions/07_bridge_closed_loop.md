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

[QUICKSTART](../appendices/QUICKSTART.md)의 환경 준비 후:

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
[Session 08](08_cobot_equipment_handover.md).

## 참고
[I1, I2, I4]: [SOURCES](../appendices/SOURCES.md).
