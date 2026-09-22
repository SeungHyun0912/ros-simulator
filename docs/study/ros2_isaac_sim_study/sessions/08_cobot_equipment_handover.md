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
[Session 09](09_test_automation_metrics.md).

## 참고
[R1] 및 본 교재 설계. [SOURCES](../appendices/SOURCES.md).
