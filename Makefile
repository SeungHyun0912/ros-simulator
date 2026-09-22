.PHONY: test check-config build mock
test:
	python3 scripts/run_unit_tests.py
check-config:
	python3 scripts/validate_fleet.py configs/fleets/poc.yaml
build:
	bash scripts/build_ros.sh
mock:
	bash scripts/run_mock.sh
