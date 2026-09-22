#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$ROOT/ros2_ws/install/setup.bash" ]]; then
  echo "먼저 ROS 환경 source 후 bash scripts/build_ros.sh를 실행하세요." >&2
  exit 2
fi
# ROS setup scripts may reference unset environment variables.
set +u
source "$ROOT/ros2_ws/install/setup.bash"
set -u
FLEET="${1:-$ROOT/configs/fleets/poc.yaml}"
if [[ $# -gt 0 ]]; then shift; fi
FLEET="$(realpath "$FLEET")"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$$"
exec ros2 launch testbed_bringup mock.launch.py   "fleet:=$FLEET" "run_id:=$RUN_ID" "$@"
