# ROS 2 · Isaac Sim 세션별 학습 자료

전체 사용법은 [README.md](README.md)를 확인하십시오.
세션별 Markdown은 `sessions/`, 실제 소스는 `examples/`에 있습니다.

1. [환경과 검증 경계](sessions/00_environment_and_scope.md)
2. [ROS 그래프와 워크스페이스](sessions/01_ros_graph_workspace.md)
3. [Topic·Service·상태](sessions/02_topics_services_state.md)
4. [Action·AMR·취소·실패](sessions/03_actions_and_mock_amr.md)
5. [QoS·동시성·시간](sessions/04_qos_concurrency_time.md)
6. [다중 로봇 Launch](sessions/05_multi_robot_launch.md)
7. [Isaac 씬·물리](sessions/06_isaac_scene_physics.md)
8. [Bridge·폐루프](sessions/07_bridge_closed_loop.md)
9. [협동로봇·설비 인계](sessions/08_cobot_equipment_handover.md)
10. [테스트와 성능 측정](sessions/09_test_automation_metrics.md)
11. [고급·운영·최종 프로젝트](sessions/10_advanced_operations_capstone.md)

각 세션은 개념·코드 해설·실습·주의사항·고급/운영 고려·완료 기준·질문과 해설로 구성됩니다.

검증 구분:
- 순수 Python 테스트: 실제 27개 통과.
- ROS 및 Isaac 실행: 미검증. 로컬 환경 확인 필요.
- 협동로봇/PLC: 스키마·로직 예제와 구현 과제.
