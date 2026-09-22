#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'ros2_ws/src/testbed_bringup'))
from testbed_bringup.fleet import load_fleet

parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('--plan', action='store_true', help='Allow unimplemented device types')
args = parser.parse_args()
data = load_fleet(args.path, require_runnable=not args.plan)
print(f"OK: {len(data['devices'])} devices; validation only, no launch")
