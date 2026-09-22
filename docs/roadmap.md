# 개발 로드맵

## 0. 저장소 적용
- README와 검증 상태 확인, 담당자/라이선스/버전 결정
- ROS 없이 순수 Python 테스트 실행
- 합격: core 테스트 통과와 설정 유효성 확인

## 1. ROS 계약 검증
- colcon build, AMR 1대 실행, move_once로 성공/취소/실패 확인
- 외부 Adapter 연결, command_id/run_id와 로그 상관관계 확인
- 합격: 접수와 완료 구분, 중복 거부, 취소 terminal 상태, 상태 Topic 일치

## 2. Isaac 1대 연결
- 버전 고정, Compatibility Checker, 부팅 스모크
- USD AMR 선택, 월드/휠 제어/Clock/cmd_vel/odom 연결
- IsaacMotion 실제 구현과 stale feedback/watchdog 추가
- 합격: 실제 위치 변화로 완료, 정지 확인, Clock 정지/리셋 시 가짜 성공 없음

## 3. 협동로봇/설비
- ExecuteTask 서버와 프로그램/인터록 정의
- 경량 상태 모델 후 관절 실행 연결
- 합격: AMR 도착/점유 조건을 만족할 때만 인계

## 4. 목표 규모
- mock 10 AMR, 이후 10+5 구성의 실제 실행 지원
- 동일 fleet를 ROS와 Isaac이 읽도록 통합
- 합격: 장비 ID/namespace 격리, 한 장비 장애의 영향 제한

## 5. 자동 회귀와 성능
- scenario YAML 실행기, batch runner, 결과 저장기 구현
- 계약/통합/복구 테스트를 CI에 추가
- GPU 실행은 별도 runner에서 수행
- 처리량, p95/p99, CPU/RSS/VRAM, RTF를 측정
- 테스트 인프라 지연과 Adapter 지연을 구분

현재 완료된 수준은 0단계 준비 코드와 1단계용 예제 코드입니다.
ROS 런타임, Isaac 연동 및 전체 목표 규모의 합격을 의미하지 않습니다.
