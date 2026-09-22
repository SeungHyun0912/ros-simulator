from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def make_nodes(context):
    count = int(LaunchConfiguration("count").perform(context))
    if not 1 <= count <= 10:
        raise ValueError("this lesson supports 1..10 AMRs")
    return [Node(
        package="study_nodes", executable="amr_server",
        namespace=f"amr_{i:02d}", name="controller", output="screen",
        parameters=[{"device_id": f"amr_{i:02d}", "backend": "mock",
                     "use_sim_time": False}],
    ) for i in range(1, count+1)]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("count", default_value="1"),
        OpaqueFunction(function=make_nodes),
    ])
