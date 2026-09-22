# 설정 적용 범위
- `fleets/poc.yaml`, `fleets/mock_amr10.yaml`: 현재 mock launch가 실제 읽습니다.
- `fleets/target_plan.yaml`: 목표 10+5대 설계 자료. 협동로봇 미구현이므로 실행 시 명시적으로 실패합니다.
- `profiles/*.yaml`, `communication/*.yaml`: 설계 참고 문서입니다. 현재 런타임이 자동으로 읽지 않습니다.
- 실행 가능한 파라미터는 launch의 `fleet`, `run_id`, `status_hz`, `fail_after_s`입니다.
- 좌표는 2D 공통 map 프레임, 미터. 회전·TF·충돌·경로 계획은 현재 범위 밖입니다.
