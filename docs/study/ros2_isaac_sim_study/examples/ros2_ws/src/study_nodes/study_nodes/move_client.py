"""Finite wall-time waits; no synchronous waiting inside ROS callbacks."""
import json
import time
import uuid
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from study_interfaces.action import MoveTo

def wait(node, future, seconds):
    end = time.monotonic() + seconds
    while rclpy.ok() and not future.done() and time.monotonic() < end:
        rclpy.spin_once(node, timeout_sec=0.05)
    if not future.done():
        raise TimeoutError("response unknown; reconcile, do not blindly retry")
    return future.result()

def main(args=None):
    rclpy.init(args=args)
    node = Node("move_client")
    defaults = {
        "task_id": "", "x": 1.0, "y": 0.0, "speed": 0.3,
        "timeout_sec": 30.0, "cancel_after_sec": -1.0,
        "output": "",
    }
    for name, value in defaults.items():
        node.declare_parameter(name, value)
    get = lambda name: node.get_parameter(name).value
    client = ActionClient(node, MoveTo, "move_to")
    handle = None
    result_future = None
    try:
        if not client.wait_for_server(timeout_sec=5.0):
            raise TimeoutError("server not found")
        goal = MoveTo.Goal()
        goal.task_id = get("task_id") or str(uuid.uuid4())
        for name in ("x", "y", "speed", "timeout_sec"):
            setattr(goal, name, float(get(name)))
        start = time.monotonic()
        handle = wait(node, client.send_goal_async(goal), 5.0)
        accepted_at = time.monotonic()
        if not handle.accepted:
            raise RuntimeError("goal rejected; inspect state and server logs")
        result_future = handle.get_result_async()
        cancel_after = float(get("cancel_after_sec"))
        cancel_sent = False
        cancel_future = None
        deadline = start + goal.timeout_sec + 10.0
        while not result_future.done() and time.monotonic() < deadline:
            if (cancel_after >= 0 and not cancel_sent and
                    time.monotonic()-accepted_at >= cancel_after):
                cancel_sent = True
                cancel_future = handle.cancel_goal_async()
            rclpy.spin_once(node, timeout_sec=0.05)
        if not result_future.done():
            raise TimeoutError("result unknown; cancellation is not confirmed")
        wrapped = result_future.result()
        row = {
            "task_id": goal.task_id, "accepted": True,
            "accept_latency_ms": (accepted_at-start)*1000,
            "completion_ms": (time.monotonic()-start)*1000,
            "status": wrapped.status,
            "success": wrapped.result.success,
            "code": wrapped.result.code,
            "cancel_sent": cancel_sent,
            "cancel_response_received": bool(cancel_future and cancel_future.done()),
        }
        print(json.dumps(row))
        if get("output"):
            with open(get("output"), "a", encoding="utf-8") as f:
                f.write(json.dumps(row)+"\n")
    finally:
        if (handle is not None and handle.accepted and
                result_future is not None and not result_future.done() and rclpy.ok()):
            # Best effort only. Do not claim this proves the robot stopped.
            try:
                wait(node, handle.cancel_goal_async(), 2.0)
            except Exception:
                pass
        client.destroy()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
