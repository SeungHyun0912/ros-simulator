#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/examples/ros2_ws/src/study_nodes${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest "$ROOT/examples/ros2_ws/src/study_nodes/test" "$ROOT/examples/pure_python/test_metrics.py" -q
python3 "$ROOT/scripts/check_python_syntax.py"
