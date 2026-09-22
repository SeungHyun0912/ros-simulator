"""Teaching-only XY proxy, NOT a wheel/contact/navigation simulator.
Standard ROS messages only. Environment must match installed Isaac Sim docs.
Run only in an isolated simulation ROS domain, never against real equipment.
Runtime NOT verified. Single process owns scene updates and ROS spin_once.
"""
import argparse
import math
import os
import time
parser=argparse.ArgumentParser()
parser.add_argument("--headless",action="store_true")
parser.add_argument("--namespace",default="amr_01")
parser.add_argument("--steps",type=int,default=0,help="0 means until closed")
args=parser.parse_args()
from isaacsim import SimulationApp
app=SimulationApp({"headless":args.headless})
node=None
ros_initialized=False
try:
    import numpy as np
    from isaacsim.core.api import World
    from isaacsim.core.api.objects import VisualCuboid
    from isaacsim.core.utils.extensions import enable_extension
    enable_extension("isaacsim.ros2.bridge")
    app.update()
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry
    from rosgraph_msgs.msg import Clock
    from builtin_interfaces.msg import Time

    rclpy.init()
    ros_initialized=True
    node=Node("kinematic_amr_bridge",namespace=args.namespace)
    received=[None,0.0,0.0]
    def command(msg):
        if math.isfinite(msg.linear.x) and math.isfinite(msg.angular.z):
            received[:]=[time.monotonic(),
                         max(-1.0,min(1.0,msg.linear.x)),
                         max(-1.0,min(1.0,msg.angular.z))]
    subscription=node.create_subscription(Twist,"cmd_vel",command,10)
    odom_pub=node.create_publisher(Odometry,"odom",10)
    # Exactly one /clock authority per test run. Do not run multiple copies
    # of this standalone script in one domain.
    clock_pub=node.create_publisher(Clock,"/clock",10)
    world=World(stage_units_in_meters=1.0,physics_dt=1/60,
                rendering_dt=1/60)
    world.scene.add_default_ground_plane()
    body=world.scene.add(VisualCuboid(
        prim_path="/World/AMRProxy",name="amr_proxy",
        position=np.array([0.0,0.0,0.2]),
        scale=np.array([0.6,0.4,0.4]),
        color=np.array([0.2,0.7,0.3])))
    world.reset()
    x=y=yaw=0.0
    step=0
    period=1/60
    next_deadline=time.monotonic()
    while app.is_running() and (args.steps==0 or step<args.steps):
        rclpy.spin_once(node,timeout_sec=0.0)
        v,w=received[1:]
        if received[0] is None or time.monotonic()-received[0]>0.5:
            v=w=0.0
        # Deliberate kinematic proxy: no collisions, wheel slip, braking dynamics.
        yaw+=w*period
        x+=v*math.cos(yaw)*period
        y+=v*math.sin(yaw)*period
        body.set_world_pose(
            position=np.array([x,y,0.2]),
            orientation=np.array([math.cos(yaw/2),0,0,math.sin(yaw/2)]))
        world.step(render=not args.headless)
        step+=1
        # Fixed-step lesson clock. Scene reset during a run is unsupported.
        ns=round(step*period*1e9)
        stamp=Time(sec=ns//1_000_000_000,nanosec=ns%1_000_000_000)
        clock=Clock(); clock.clock=stamp; clock_pub.publish(clock)
        odom=Odometry()
        odom.header.stamp=stamp
        odom.header.frame_id="map"
        odom.child_frame_id=args.namespace.strip("/")+"/base_link"
        odom.pose.pose.position.x=x
        odom.pose.pose.position.y=y
        odom.pose.pose.orientation.z=math.sin(yaw/2)
        odom.pose.pose.orientation.w=math.cos(yaw/2)
        odom.twist.twist.linear.x=v
        odom.twist.twist.angular.z=w
        odom_pub.publish(odom)
        # Best-effort real-time pacing, not a real-time guarantee.
        next_deadline+=period
        delay=next_deadline-time.monotonic()
        if delay>0:
            time.sleep(delay)
        elif delay < -1.0:
            next_deadline=time.monotonic()
finally:
    if node is not None:
        node.destroy_node()
    if ros_initialized and rclpy.ok():
        rclpy.shutdown()
    app.close()
