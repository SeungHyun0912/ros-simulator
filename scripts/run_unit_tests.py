#!/usr/bin/env python3
"""Pure Python tests only; no ROS/Isaac/PyYAML requirement."""
from pathlib import Path
import sys
import unittest

root = Path(__file__).resolve().parents[1]
for package in ('testbed_backends', 'testbed_devices'):
    sys.path.insert(0, str(root / 'ros2_ws' / 'src' / package))
suite = unittest.defaultTestLoader.discover(str(root / 'tests' / 'unit'))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
