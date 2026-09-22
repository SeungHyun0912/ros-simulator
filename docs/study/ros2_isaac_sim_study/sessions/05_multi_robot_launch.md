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
[Session 06](06_isaac_scene_physics.md).

## 참고
노드/인터페이스 개념 [R1], 구현은 본 교재 제안. [SOURCES](../appendices/SOURCES.md).
