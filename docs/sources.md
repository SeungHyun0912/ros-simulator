# 공식 참고 문서
2026-09-21 문서 확인. API/패키징 참고용이며 이 템플릿 코드의 실행 검증을 대체하지 않습니다.
`latest` 페이지는 변경될 수 있으므로 실제 채택 시 버전 문서 링크로 고정하세요.

- ROS 2 Jazzy 사용자 정의 인터페이스 패키징:
  https://repo.test.ros2.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html
- ROS 2 Jazzy rosidl_default_generators:
  https://docs.ros.org/en/jazzy/p/rosidl_default_generators/
- Isaac Sim Python 실행 환경:
  https://docs.isaacsim.omniverse.nvidia.com/latest/python_scripting/manual_standalone_python.html
- Isaac Sim ROS 2 Bridge standalone:
  https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/bridge_configuration/tutorial_ros2_python.html

문서에서 파생한 요점:
- 사용자 정의 인터페이스는 별도 rosidl 빌드 패키지로 생성합니다.
- Isaac 관련 앱 초기화와 ROS Bridge 구성은 설치 버전의 실행 환경에 맞춰야 합니다.

ROS Action 예제 공식 페이지는 조회 시 접근 제한이 있어 내용 확인에 사용하지 않았습니다.
ROS Action 서버 코드는 생성한 시작 예제로, 실제 ROS 환경에서 검증해야 합니다.
