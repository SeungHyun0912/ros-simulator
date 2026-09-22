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
