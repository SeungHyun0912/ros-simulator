"""Small ROS action smoke client; not an Adapter implementation."""
import argparse
import json
import time
import uuid

import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node
from testbed_interfaces.action import MoveTo


def wait(node, future, timeout):
    deadline = time.monotonic() + timeout
    while rclpy.ok() and not future.done():
        if time.monotonic() >= deadline:
            raise TimeoutError('ROS response timeout')
        rclpy.spin_once(node, timeout_sec=0.05)
    if not future.done():
        raise RuntimeError('ROS shutdown')
    return future.result()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--namespace', default='/amr_01')
    parser.add_argument('--x', type=float, default=2.0)
    parser.add_argument('--y', type=float, default=0.0)
    parser.add_argument('--command-id', default=None)
    parser.add_argument('--timeout', type=float, default=30.0)
    parser.add_argument('--cancel-after', type=float, default=None)
    parser.add_argument('--expect', choices=['succeeded', 'canceled', 'aborted', 'rejected'],
                        default='succeeded')
    args = parser.parse_args()
    if args.timeout <= 0 or (args.cancel_after is not None and args.cancel_after < 0):
        parser.error('invalid timeout/cancel delay')
    rclpy.init(args=[])
    node = Node('testbed_move_once')
    client = ActionClient(node, MoveTo, args.namespace.rstrip('/') + '/move_to')
    handle = None
    started = time.monotonic()
    exit_code = 1
    try:
        if not client.wait_for_server(timeout_sec=5.0):
            raise TimeoutError('move_to server unavailable')
        goal = MoveTo.Goal()
        goal.command_id = args.command_id or str(uuid.uuid4())
        goal.target_x, goal.target_y = args.x, args.y
        handle = wait(node, client.send_goal_async(goal), args.timeout)
        if not handle.accepted:
            observed = 'rejected'
            detail = 'No action result on rejected goal'
        else:
            result_future = handle.get_result_async()
            accepted_at = time.monotonic()
            cancel_sent = False
            while rclpy.ok() and not result_future.done():
                elapsed = time.monotonic() - accepted_at
                if elapsed > args.timeout:
                    # Best effort only: verify terminal state externally after timeout.
                    handle.cancel_goal_async()
                    rclpy.spin_once(node, timeout_sec=0.1)
                    raise TimeoutError('result timeout; cancellation requested')
                if (args.cancel_after is not None and not cancel_sent
                        and elapsed >= args.cancel_after):
                    handle.cancel_goal_async()
                    cancel_sent = True
                rclpy.spin_once(node, timeout_sec=0.05)
            if not result_future.done():
                raise RuntimeError('ROS shutdown before result')
            response = result_future.result()
            observed = {
                GoalStatus.STATUS_SUCCEEDED: 'succeeded',
                GoalStatus.STATUS_CANCELED: 'canceled',
                GoalStatus.STATUS_ABORTED: 'aborted',
            }.get(response.status, 'unknown')
            detail = response.result.detail
        exit_code = 0 if observed == args.expect else 1
        print(json.dumps({
            'command_id': goal.command_id, 'observed': observed,
            'expected': args.expect, 'passed': exit_code == 0, 'detail': detail,
            'elapsed_s': time.monotonic() - started,
        }, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({'passed': False, 'error': str(exc)}, ensure_ascii=False))
    finally:
        client.destroy()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    raise SystemExit(exit_code)
