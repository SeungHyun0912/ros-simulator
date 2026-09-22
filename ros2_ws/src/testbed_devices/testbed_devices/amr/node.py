import json
import math
import threading
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from testbed_interfaces.action import MoveTo
from testbed_interfaces.msg import DeviceState
from testbed_backends.mock import MockMotion
from testbed_devices.common.controller import DeviceController


class AmrNode(Node):
    """One process/node per device; wall-clock mock only."""

    def __init__(self):
        super().__init__('amr_controller')
        defaults = {
            'device_id': 'amr_01', 'run_id': 'manual',
            'backend': 'mock', 'initial_x': 0.0, 'initial_y': 0.0,
            'speed_mps': 1.0, 'status_hz': 5.0,
            'fail_after_s': -1.0,
        }
        for key, value in defaults.items():
            self.declare_parameter(key, value)
        p = lambda key: self.get_parameter(key).value
        if p('backend') != 'mock':
            raise RuntimeError('Only mock is implemented; Isaac backend is TODO')
        if self.has_parameter('use_sim_time') and p('use_sim_time'):
            raise RuntimeError('Mock node requires use_sim_time=false')
        hz = float(p('status_hz'))
        self.fail_after = float(p('fail_after_s'))
        if not math.isfinite(hz) or hz <= 0 or not math.isfinite(self.fail_after):
            raise ValueError('invalid rate or fault time')
        self.device_id, self.run_id = str(p('device_id')), str(p('run_id'))
        self.controller = DeviceController(MockMotion(
            float(p('initial_x')), float(p('initial_y')), float(p('speed_mps'))))
        self._lock = threading.Lock()
        self._busy = False
        self._seen = set()
        self._group = ReentrantCallbackGroup()
        qos = QoSProfile(
            depth=10, reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE)
        self.publisher = self.create_publisher(DeviceState, 'state', qos)
        self.server = ActionServer(
            self, MoveTo, 'move_to',
            execute_callback=self.execute,
            goal_callback=self.accept_goal,
            cancel_callback=self.accept_cancel,
            callback_group=self._group)
        self.timer = self.create_timer(
            1.0 / hz, self.publish_state, callback_group=self._group)

    def event(self, name, command_id='', code=''):
        self.get_logger().info(json.dumps({
            'event': name, 'device_id': self.device_id,
            'command_id': command_id, 'run_id': self.run_id,
            'wall_time_ns': time.time_ns(), 'monotonic_ns': time.monotonic_ns(),
            'error_code': code,
        }))

    def accept_goal(self, request):
        with self._lock:
            invalid = (not request.command_id.strip()
                       or not math.isfinite(request.target_x)
                       or not math.isfinite(request.target_y))
            if self._busy or invalid or request.command_id in self._seen:
                self.event('rejected', request.command_id, 'BUSY_INVALID_OR_DUPLICATE')
                return GoalResponse.REJECT
            self._busy = True
            self._seen.add(request.command_id)
            self.event('accepted', request.command_id)
            return GoalResponse.ACCEPT

    def accept_cancel(self, goal_handle):
        self.event('cancel_requested', goal_handle.request.command_id)
        return CancelResponse.ACCEPT

    def publish_state(self):
        with self._lock:
            c = self.controller
            snap = c.backend.snapshot()
            msg = DeviceState()
            msg.stamp = self.get_clock().now().to_msg()
            msg.run_id, msg.device_id = self.run_id, self.device_id
            msg.command_id, msg.status = c.command_id, c.status
            msg.x, msg.y, msg.error_code = snap.x, snap.y, c.error_code
        self.publisher.publish(msg)

    def execute(self, goal_handle):
        request = goal_handle.request
        result = MoveTo.Result()
        started = previous = time.monotonic()
        try:
            with self._lock:
                self.controller.start(
                    request.command_id, request.target_x, request.target_y)
            while rclpy.ok():
                now = time.monotonic()
                with self._lock:
                    c = self.controller
                    # In this example: cancellation > injected fault > completion.
                    if goal_handle.is_cancel_requested:
                        c.cancel()
                        goal_handle.canceled()
                        result.success, result.error_code = False, 'CANCELED'
                        break
                    if self.fail_after >= 0 and now - started >= self.fail_after:
                        c.fail()
                        goal_handle.abort()
                        result.success, result.error_code = False, 'INJECTED'
                        break
                    snap = c.tick(now - previous)
                    if snap.done:
                        goal_handle.succeed()
                        result.success, result.error_code = True, ''
                        break
                previous = now
                feedback = MoveTo.Feedback()
                feedback.x, feedback.y = snap.x, snap.y
                feedback.progress = float(snap.progress)
                goal_handle.publish_feedback(feedback)
                time.sleep(0.05)
            else:
                with self._lock:
                    self.controller.fail('SHUTDOWN')
                if goal_handle.is_active:
                    goal_handle.abort()
                result.success, result.error_code = False, 'SHUTDOWN'
            result.detail = result.error_code or 'Arrived (mock, no physics)'
        except Exception as exc:
            with self._lock:
                self.controller.fail('INTERNAL')
            if goal_handle.is_active:
                goal_handle.abort()
            result.success, result.error_code = False, 'INTERNAL'
            result.detail = str(exc)
        finally:
            with self._lock:
                self._busy = False
        self.event('finished', request.command_id, result.error_code)
        return result


def main(args=None):
    rclpy.init(args=args)
    node = None
    executor = MultiThreadedExecutor(num_threads=4)
    try:
        node = AmrNode()
        executor.add_node(node)
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
