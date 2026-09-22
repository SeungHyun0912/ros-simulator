#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ROS_DISTRO:-}" ]]; then
  echo "먼저 ROS 환경을 source 하세요. 예: source /opt/ros/jazzy/setup.bash" >&2
  exit 2
fi
command -v colcon >/dev/null || { echo "colcon 필요" >&2; exit 2; }
cd "$ROOT/ros2_ws"
colcon build --symlink-install "$@"
