# Isaac Sim 영역 — 확장 골격
현재 `apps/smoke_app.py`만 부팅 확인용 예제로 제공합니다.
이 스크립트는 로봇·물리 World·Clock·ROS Bridge를 생성하지 않습니다.
Headless는 창을 숨기는 옵션일 뿐, 모든 렌더링이 비활성화됐다고 간주하면 안 됩니다.

## 실행 전
1. 사용할 Isaac Sim 버전을 선정하고 공식 지원 OS/드라이버/ROS 조합을 확인합니다.
2. 해당 설치 방식의 Python 실행 환경을 준비합니다.
3. 설치 제공 `python.sh`가 있는 경우:
   `"$ISAAC_SIM_PATH/python.sh" isaac_sim/apps/smoke_app.py --headless --frames 60`
4. pip 설치 방식이면 그 설치에 맞는 환경의 Python으로 동일 스크립트를 실행합니다.
5. 현재 템플릿은 Isaac 실행 검증을 받지 않았습니다. API 변경 시 선택한 버전 문서에 맞춰 조정하세요.

## 실제 연결 작업 순서
- worlds: 바닥과 AMR 1대 생성, 모델/조인트/휠 축 확인
- bridges: `/clock`, `/<id>/cmd_vel`, `/<id>/odom` 연결 및 주기/QoS 확정
- robots: Twist를 차륜 명령으로 연결, 측정 상태에서 odometry 생성
- ROS backend: odometry 기반 도착 판정, stale 상태/Clock 정지/취소 처리
- runtime: 시작·정지·리셋과 run_id 전환
- tests: 동일 명령의 mock/Isaac 의미 일치와 실제 이동 확인

이 작업이 끝나기 전 Isaac backend를 선택하면 명시적으로 실패해야 합니다.
ROS Action 접수만으로 성공을 반환하지 않습니다.
