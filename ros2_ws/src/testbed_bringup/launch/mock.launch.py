import math
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from testbed_bringup.fleet import load_fleet


def build_nodes(context):
    path = Path(LaunchConfiguration('fleet').perform(context)).expanduser()
    if not path.is_file():
        raise ValueError(f'Fleet file does not exist: {path}')
    fleet = load_fleet(path, require_runnable=True)
    run_id = LaunchConfiguration('run_id').perform(context)
    fail_after = float(LaunchConfiguration('fail_after_s').perform(context))
    status_hz = float(LaunchConfiguration('status_hz').perform(context))
    if not math.isfinite(fail_after) or not math.isfinite(status_hz) or status_hz <= 0:
        raise ValueError('Invalid status_hz or fail_after_s')
    nodes = []
    for device in fleet['devices']:
        x, y = device.get('initial_position', [0.0, 0.0])
        nodes.append(Node(
            package='testbed_devices', executable='amr_node',
            namespace=device['namespace'], name='controller', output='screen',
            parameters=[{
                'device_id': device['device_id'], 'run_id': run_id,
                'backend': 'mock', 'initial_x': float(x), 'initial_y': float(y),
                'speed_mps': float(device.get('speed_mps', 1.0)),
                'status_hz': status_hz, 'fail_after_s': fail_after,
                'use_sim_time': False,
            }]))
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('fleet', description='Absolute fleet YAML path'),
        DeclareLaunchArgument('run_id', default_value='manual'),
        DeclareLaunchArgument('fail_after_s', default_value='-1.0'),
        DeclareLaunchArgument('status_hz', default_value='5.0'),
        OpaqueFunction(function=build_nodes),
    ])
