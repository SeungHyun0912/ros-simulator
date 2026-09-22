#!/usr/bin/env python3
"""Isaac application boot check ONLY. No physics world/robot/ROS graph."""
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--headless', action='store_true')
parser.add_argument('--frames', type=int, default=60)
args = parser.parse_args()
if args.frames <= 0:
    parser.error('--frames must be positive')

# Run with the selected Isaac installation's Python, not system Python.
from isaacsim import SimulationApp

app = SimulationApp({'headless': args.headless})
try:
    for _ in range(args.frames):
        if not app.is_running():
            break
        app.update()
    print('BOOT CHECK finished. NOT a robot/physics/ROS integration test.')
finally:
    app.close()
