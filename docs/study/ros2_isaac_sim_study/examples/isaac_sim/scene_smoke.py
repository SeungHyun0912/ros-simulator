"""Version-sensitive Core API sample; execute with Isaac Sim Python, not OS Python.
Runtime NOT verified in the supplied environment. No external robot asset needed.
"""
import argparse
parser=argparse.ArgumentParser()
parser.add_argument("--headless",action="store_true")
parser.add_argument("--steps",type=int,default=300)
args=parser.parse_args()
from isaacsim import SimulationApp
app=SimulationApp({"headless":args.headless})
try:
    # Isaac-dependent imports belong AFTER SimulationApp initialization.
    import numpy as np
    from isaacsim.core.api import World
    from isaacsim.core.api.objects import DynamicCuboid
    world=World(stage_units_in_meters=1.0)
    world.scene.add_default_ground_plane()
    cube=world.scene.add(DynamicCuboid(
        prim_path="/World/TestBox", name="test_box",
        position=np.array([0.0,0.0,1.0]), size=0.2,
        color=np.array([0.2,0.6,0.8])))
    world.reset()
    for i in range(args.steps):
        world.step(render=not args.headless)
    p,q=cube.get_world_pose()
    print("final position (m):",p,"orientation (wxyz):",q)
    # Record observed result. This file does not claim a physics tolerance test.
finally:
    app.close()
