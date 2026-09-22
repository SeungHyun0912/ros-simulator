"""ROS 2 teaching Action server. Runtime validation on Jazzy is still required."""
import math
import threading
import time
import uuid
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import SingleThreadedExecutor
from rclpy.clock import Clock
from rclpy.clock_type import ClockType
from rclpy.task import Future
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger, SetBool
from study_interfaces.action import MoveTo
from study_interfaces.msg import DeviceState
from .core import Motion, Request

class AMRServer(Node):
    def __init__(self):
        super().__init__("amr_server")
        self.declare_parameter("device_id", "amr_01")
        self.declare_parameter("backend", "mock")
        self.declare_parameter("pose_timeout_sec", 1.0)
        self.device_id = self.get_parameter("device_id").value
        self.backend = self.get_parameter("backend").value
        if self.backend not in ("mock", "odom"):
            raise ValueError("backend must be mock or odom")
        self.pose_timeout = float(self.get_parameter("pose_timeout_sec").value)
        if not math.isfinite(self.pose_timeout) or self.pose_timeout <= 0:
            raise ValueError("pose_timeout_sec must be finite and positive")
        self.boot_id = str(uuid.uuid4())
        self.sequence = 0
        self.motion = Motion()
        self.lock = threading.RLock()
        self.group = ReentrantCallbackGroup()
        self.active = None
        self.futures = {}
        self.faulted = False
        self.pose_received = None
        self.yaw = 0.0
        self.last_tick = time.monotonic()
        reliable = QoSProfile(depth=10,
                             reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.VOLATILE)
        self.state_pub = self.create_publisher(DeviceState, "state", reliable)
        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", reliable)
        self.odom_sub = self.create_subscription(
            Odometry, "odom", self.on_odom,
            QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT),
            callback_group=self.group)
        self.reset_srv = self.create_service(
            Trigger, "reset_idle", self.reset_idle, callback_group=self.group)
        self.fault_srv = self.create_service(
            SetBool, "test/set_fault", self.set_fault, callback_group=self.group)
        self.action = ActionServer(
            self, MoveTo, "move_to", execute_callback=self.execute,
            goal_callback=self.goal, cancel_callback=self.cancel,
            handle_accepted_callback=self.accepted, callback_group=self.group,
            result_timeout=60.0)
        # A stopped simulation clock must not stop communication watchdogs.
        steady = Clock(clock_type=ClockType.STEADY_TIME)
        self.tick_timer = self.create_timer(
            0.05, self.tick, callback_group=self.group, clock=steady)
        self.state_timer = self.create_timer(
            0.2, self.publish_state, callback_group=self.group, clock=steady)

    def on_odom(self, msg):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        values = (p.x, p.y, q.x, q.y, q.z, q.w)
        if not all(math.isfinite(v) for v in values):
            return
        norm = math.sqrt(q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w)
        if norm < 1e-9:
            return
        x, y, z, w = q.x/norm, q.y/norm, q.z/norm, q.w/norm
        with self.lock:
            if self.backend == "odom":
                self.motion.observe(p.x, p.y)
                self.yaw = math.atan2(2*(w*z+x*y), 1-2*(y*y+z*z))
                self.pose_received = time.monotonic()

    def goal(self, msg):
        with self.lock:
            if self.active is not None or self.faulted:
                return GoalResponse.REJECT
            if self.backend == "odom":
                if (self.pose_received is None or
                    time.monotonic()-self.pose_received > self.pose_timeout):
                    return GoalResponse.REJECT
            try:
                self.motion.start(Request(msg.task_id, msg.x, msg.y,
                                          msg.speed, msg.timeout_sec))
            except ValueError as exc:
                self.get_logger().warning(f"REJECT: {exc}")
                return GoalResponse.REJECT
            self.last_tick = time.monotonic()
            return GoalResponse.ACCEPT

    @staticmethod
    def key(handle):
        return bytes(handle.goal_id.uuid)

    def accepted(self, handle):
        with self.lock:
            self.active = handle
            self.futures[self.key(handle)] = Future()
        handle.execute()

    async def execute(self, handle):
        key = self.key(handle)
        try:
            return await self.futures[key]
        finally:
            self.futures.pop(key, None)

    def cancel(self, handle):
        with self.lock:
            if handle is self.active and self.motion.busy:
                return CancelResponse.ACCEPT
            return CancelResponse.REJECT

    def reset_idle(self, request, response):
        with self.lock:
            if self.active is not None:
                response.success, response.message = False, "BUSY"
                return response
            try:
                self.motion.reset_idle()
                response.success, response.message = True, "IDLE; pose/ledger kept"
            except ValueError as exc:
                response.success, response.message = False, str(exc)
        return response

    def set_fault(self, request, response):
        with self.lock:
            self.faulted = request.data
            response.success = True
            response.message = "fault flag updated; not a physical emergency stop"
        return response

    def drive(self):
        req = self.motion.request
        heading = math.atan2(req.y-self.motion.y, req.x-self.motion.x)
        error = (heading-self.yaw+math.pi) % (2*math.pi)-math.pi
        cmd = Twist()
        cmd.angular.z = max(-1.0, min(1.0, 2.0*error))
        if abs(error) < 0.3:
            cmd.linear.x = min(req.speed, self.motion.remaining)
        self.cmd_pub.publish(cmd)

    def tick(self):
        now = time.monotonic()
        dt, self.last_tick = now-self.last_tick, now
        with self.lock:
            handle = self.active
            if handle is None:
                return
            # Priority for this lesson: cancellation > injected fault > timeout/arrival.
            if handle.is_cancel_requested:
                self.motion.cancel()
            elif self.faulted:
                self.motion.fail("INJECTED_FAULT")
            elif (self.backend == "odom" and
                  (self.pose_received is None or
                   now-self.pose_received > self.pose_timeout)):
                self.motion.fail("STALE_POSE")
            else:
                self.motion.tick(dt, integrate=self.backend == "mock")

            if self.motion.busy:
                if self.backend == "odom":
                    self.drive()
                feedback = MoveTo.Feedback()
                feedback.remaining_m = self.motion.remaining
                feedback.phase = self.motion.phase
                handle.publish_feedback(feedback)
                return

            self.cmd_pub.publish(Twist())
            result = MoveTo.Result()
            result.success = self.motion.phase == "SUCCEEDED"
            result.code = self.motion.detail
            result.detail = "teaching backend=" + self.backend
            if result.success:
                handle.succeed()
            elif self.motion.phase == "CANCELED":
                handle.canceled()
            else:
                handle.abort()
            future = self.futures[self.key(handle)]
            self.active = None
            future.set_result(result)

    def publish_state(self):
        with self.lock:
            msg = DeviceState()
            msg.stamp = self.get_clock().now().to_msg()
            msg.device_id, msg.boot_id = self.device_id, self.boot_id
            self.sequence += 1
            msg.sequence = self.sequence
            msg.task_id = self.motion.request.task_id if self.motion.request else ""
            msg.phase = self.motion.phase
            msg.x, msg.y = self.motion.x, self.motion.y
            msg.detail = self.motion.detail
            self.state_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AMRServer()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        # Best effort shutdown; backend-side command watchdog remains necessary.
        if rclpy.ok():
            node.cmd_pub.publish(Twist())
        executor.shutdown()
        node.action.destroy()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
