# 공식 자료·버전·확인 범위

문서 확인 기준: 2026-09-21 KST. 아래 URL의 `latest`는 향후 변경될 수 있습니다.
단순 링크 나열이 아니라, 각 세션에서 근거를 사용하는 범위를 표시했습니다.
배포판이 다른 개념 문서는 개념 설명만 참고하며 Jazzy API 호환성을 검증한 것으로 해석하지 않습니다.

## ROS 2

- **[R1] Topic / Service / Action 개념 — 공식 Kilted 개념 문서 확인**
  https://docs.ros.org/en/ros2_documentation/kilted/How-To-Guides/Topics-Services-Actions.html
  사용 범위: 스트림, 짧은 RPC, 장시간 취소 가능한 작업의 역할 구분.
- **[R2] Jazzy Python Action 공식 패키지 페이지 확인**
  https://docs.ros.org/en/jazzy/p/action_tutorials_py/index.html
  사용 범위: Action 서버/클라이언트 API 학습 진입점. 본 코드 전체의 실행 보증 자료가 아님.
- **[R3] Callback Groups — 공식 Kilted 문서 확인**
  https://docs.ros.org/en/ros2_documentation/kilted/How-To-Guides/Using-callback-groups.html
  사용 범위: 상호배제/재진입 그룹, 실행기와 교착. Jazzy에서는 설치된 API로 추가 확인.
- **[R4] QoS — 공식 Humble 개념 문서 검색 결과 확인**
  https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html
  사용 범위: QoS 호환성 개념. Jazzy 실습의 상세 값은 실제 endpoint에서 확인.
- **[R5] Jazzy Service Python 공식 문서 검색 결과 확인**
  https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html
  사용 범위: 비동기 요청, 콜백 내부 spin_until_future_complete 회피.
- **[R6] 공식 Python Action 예제의 역사적 설명 확인**
  https://docs.ros.org/en/dashing/Tutorials/Actions/Writing-a-Py-Action-Server-Client.html
  Dashing은 지원 종료 배포판. 설치/런타임 기준으로 사용하지 않음.
  사용 범위: GoalHandle·Feedback·Result의 개념만 교차 확인.

### 학습자가 추가 확인할 Jazzy 원문 (이번 조회에서 접근 차단)

다음 페이지는 도구 조회가 Access Denied였으므로 본문을 확인했다고 주장하지 않습니다.
브라우저에서 접근되면 설치 버전 기준으로 API를 확인하십시오.

- https://docs.ros.org/en/jazzy/How-To-Guides/Topics-Services-Actions.html
- https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html
- https://docs.ros.org/en/jazzy/How-To-Guides/Using-callback-groups.html
- https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html
- https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html
- https://docs.ros.org/en/jazzy/p/rclpy/rclpy.action.server.html
- https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html

## Isaac Sim

- **[I0] 5.1 Standalone 문서와 지원 종료 배너 확인**
  https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ros2_tutorials/tutorial_ros2_python.html
  사용 범위: 5.1을 최신·지원 버전으로 추천하지 않는 이유.
- **[I1] 현재 ROS 2 설치 구성 안내**
  https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html
  사용 범위: Ubuntu 24.04/Jazzy 경로, 표준/사용자 정의 인터페이스,
  Isaac 런타임 Python과 외부 ROS 환경의 구분.
- **[I2] 현재 Standalone ROS 2 Bridge 문서**
  https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/bridge_configuration/tutorial_ros2_python.html
  사용 범위: SimulationApp 기반 워크플로·Bridge·Clock·manual stepping.
- **[I3] 현재 성능 최적화 안내**
  https://docs.isaacsim.omniverse.nvidia.com/latest/reference_material/sim_performance_optimization_handbook.html
  사용 범위: 렌더링·물리 비용을 구분하여 최적화하는 접근.
- **[I4] Core API Hello World, 5.1 보관 문서**
  https://docs.isaacsim.omniverse.nvidia.com/5.1.0/core_api_tutorials/tutorial_core_hello_world.html
  사용 범위: World/큐브/시뮬레이션 단계의 기본 구조.
  예제의 최신 API 실행 여부는 확인하지 않았습니다. 설치 버전에서 import 경로를 확인합니다.
- **[I5] 현재 설치 진입점**
  https://docs.isaacsim.omniverse.nvidia.com/latest/installation/quick-install.html
  다운로드·설치 경로 확인용. 교재가 특정 신규 릴리스의 안정성을 보증하지 않습니다.

## 해석 주의

- 교재의 0.05s 주기, 1s watchdog, 0.03m 도착 판정은 **학습용 설정값**입니다.
- 성능 수치·학습 시간·권장 아키텍처는 제품의 공식 보증 수치가 아닙니다.
- 출처 코드의 장문 복제 대신 독립된 학습 코드를 구성했습니다.
- 문서 링크의 버전과 실제 설치 버전을 환경 매니페스트에 함께 기록합니다.
