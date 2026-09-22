#!/usr/bin/env bash
set -eu
echo "=== OS ==="
uname -a
echo "=== ROS environment (informational) ==="
echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-default}"
echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-default}"
echo "=== Python ==="
python3 --version
echo "=== NVIDIA GPU (if installed) ==="
if command -v nvidia-smi >/dev/null; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
else
  echo "nvidia-smi not found; GPU/Isaac compatibility NOT assessed"
fi
echo "=== Important ==="
echo "This script is informational, not the NVIDIA Compatibility Checker."
