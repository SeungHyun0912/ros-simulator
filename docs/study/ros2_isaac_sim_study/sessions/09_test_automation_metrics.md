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
[Session 10](10_advanced_operations_capstone.md).

## 참고
본 세션 지표와 절차는 프로젝트 설계입니다.
ROS 문서 확인 범위: [SOURCES](../appendices/SOURCES.md).
