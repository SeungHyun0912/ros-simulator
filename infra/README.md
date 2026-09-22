# 실행 환경
현재 Dockerfile/Compose는 제공하지 않습니다.
ROS/Isaac/드라이버 버전을 결정한 뒤 서로 다른 실행 환경으로 구성하세요.
컨테이너화 시 GPU 전달, DDS discovery, ROS_DOMAIN_ID, 네트워크 범위,
공통 RMW 설정 및 라이선스 조건을 검증해야 합니다.
먼저 네이티브 ROS mock 실행을 확인하고 그 다음 컨테이너화하세요.
