"""Wall-time heartbeat observer; silence is UNKNOWN, not IDLE."""
import time
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock
from rclpy.clock_type import ClockType
from rclpy.qos import QoSProfile, ReliabilityPolicy
from study_interfaces.msg import DeviceState

class Watch(Node):
    def __init__(self):
        super().__init__("state_watch")
        self.last = None
        self.boot = None
        self.seq = None
        self.stale = False
        self.sub = self.create_subscription(
            DeviceState, "state", self.receive,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE))
        self.timer = self.create_timer(
            0.2, self.check, clock=Clock(clock_type=ClockType.STEADY_TIME))

    def receive(self, msg):
        if self.boot is not None and self.boot != msg.boot_id:
            self.get_logger().warning("RESTART: reconcile active tasks")
            self.seq = None
        if self.seq is not None and msg.sequence <= self.seq:
            self.get_logger().warning("non-increasing sequence")
        self.boot, self.seq = msg.boot_id, msg.sequence
        self.last, self.stale = time.monotonic(), False
        self.get_logger().info(f"{msg.device_id} {msg.phase} seq={msg.sequence}")

    def check(self):
        if self.last is None:
            return
        if time.monotonic()-self.last > 1.0 and not self.stale:
            self.stale = True
            self.get_logger().warning("UNKNOWN: heartbeat stale, not IDLE")

def main(args=None):
    rclpy.init(args=args)
    node = Watch()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
