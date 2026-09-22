# 환경 기준과 검증 상태
작성일: 2026-09-21 (Asia/Seoul).

## 초기 개발 기준안
- ROS 영역: Ubuntu 24.04 + ROS 2 Jazzy를 기본 문서 예시로 사용합니다.
- 다른 ROS 배포판을 쓰려면 패키지 의존성과 런타임을 별도 검증하세요.
- Isaac Sim: 특정 버전 미선정. 설치할 버전과 ROS 조합을 확인한 후 고정합니다.
- 본 템플릿은 ROS와 Isaac Sim이 설치되지 않은 환경에서 생성했습니다.
- 최신 릴리스 보장이나 OS/GPU 호환성 인증을 의미하지 않습니다.

## 필수 기록
실제 검증 후 OS, ROS, Python, Isaac, NVIDIA 드라이버, GPU/VRAM,
RMW, 실행 날짜, Git commit을 이 문서 또는 검증 보고서에 기록하세요.
현재 환경 조합 값은 미확정이며 lockfile로 가장하지 않습니다.

## 설치 원칙
- ROS는 해당 배포판 설치 문서와 rosdep을 사용합니다.
- rclpy를 일반 pip 환경에 무조건 설치하려 하지 않습니다.
- requirements-dev.txt는 YAML 검증 스크립트용 개발 의존성만 포함합니다.
- Isaac 자체 설치와 Python 실행 환경은 이 저장소에 포함하지 않습니다.
- ROS와 Isaac 환경을 하나의 venv로 억지로 통합하지 않습니다.
- 외부 PC Adapter와 ROS 노드는 같은 인터페이스 정의와 통신 설정을 사용해야 합니다.

## 네트워크
개발용 격리망에서 시작하세요. ROS_DOMAIN_ID가 동일해야 서로 발견할 수 있으며,
Domain ID 자체는 보안 경계가 아닙니다.
배포판별 discovery/RMW/멀티캐스트/방화벽 설정을 검증하세요.
공개 인터넷에 시험용 명령 엔드포인트를 그대로 노출하지 마세요.
