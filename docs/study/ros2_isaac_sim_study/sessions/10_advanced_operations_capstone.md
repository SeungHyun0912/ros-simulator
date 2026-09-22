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

운영 상세: [OPERATIONS_CHECKLIST](../appendices/OPERATIONS_CHECKLIST.md).

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
[I1, I2, I3]의 기반 문서: [SOURCES](../appendices/SOURCES.md).
