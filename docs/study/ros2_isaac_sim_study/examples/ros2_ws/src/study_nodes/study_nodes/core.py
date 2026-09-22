"""Pure Python teaching model. No ROS, GPU or vendor dependencies."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Request:
    task_id: str
    x: float
    y: float
    speed: float = 0.3
    timeout_sec: float = 30.0

class Motion:
    """One active task; bounded in-memory duplicate rejection, not durable dedup."""
    def __init__(self, tolerance=0.03, capacity=1024):
        if not math.isfinite(tolerance) or tolerance <= 0 or capacity < 1:
            raise ValueError("invalid model configuration")
        self.tolerance = tolerance
        self.capacity = capacity
        self.seen = set()
        self.x = self.y = self.elapsed = 0.0
        self.phase = "IDLE"
        self.detail = ""
        self.request = None

    @property
    def busy(self):
        return self.phase == "RUNNING"

    @property
    def remaining(self):
        if self.request is None:
            return 0.0
        return math.hypot(self.request.x-self.x, self.request.y-self.y)

    def observe(self, x, y):
        if not all(math.isfinite(v) for v in (x, y)):
            raise ValueError("invalid pose")
        self.x, self.y = float(x), float(y)

    def start(self, request):
        if self.busy:
            raise ValueError("BUSY")
        if not request.task_id or len(request.task_id) > 128:
            raise ValueError("INVALID_TASK_ID")
        if not all(math.isfinite(v) for v in
                   (request.x, request.y, request.speed, request.timeout_sec)):
            raise ValueError("NON_FINITE")
        if not 0 < request.speed <= 1.0 or not 0 < request.timeout_sec <= 3600.0:
            raise ValueError("OUT_OF_RANGE")
        if abs(request.x) > 100 or abs(request.y) > 100:
            raise ValueError("OUT_OF_WORKSPACE")
        if request.task_id in self.seen:
            raise ValueError("DUPLICATE")
        if len(self.seen) >= self.capacity:
            raise ValueError("LEDGER_FULL")  # fail closed, do not evict silently
        self.seen.add(request.task_id)
        self.request = request
        self.elapsed = 0.0
        self.phase, self.detail = "RUNNING", ""

    def tick(self, dt, *, integrate=True):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("invalid dt")
        if not self.busy:
            return
        self.elapsed += dt
        # Explicit policy: wall-time timeout wins over arrival on the same tick.
        if self.elapsed >= self.request.timeout_sec:
            self.fail("TIMEOUT")
            return
        if integrate and self.remaining > 0:
            distance = self.remaining
            step = min(self.request.speed*dt, distance)
            self.x += (self.request.x-self.x)*step/distance
            self.y += (self.request.y-self.y)*step/distance
        if self.remaining <= self.tolerance:
            self.phase, self.detail = "SUCCEEDED", "ARRIVED"

    def cancel(self):
        if self.busy:
            self.phase, self.detail = "CANCELED", "CANCEL_REQUESTED"

    def fail(self, reason):
        if self.busy:
            self.phase, self.detail = "FAILED", reason

    def reset_idle(self):
        if self.busy:
            raise ValueError("BUSY")
        self.phase, self.detail = "IDLE", ""
        self.request = None
        # Position and duplicate ledger intentionally survive soft reset.

@dataclass(frozen=True)
class Interlock:
    """Simplified cell gate, not a safety function."""
    docked: bool
    amr_stopped: bool
    arm_ready: bool
    output_clear: bool
    communication_fresh: bool

    def ready(self):
        return all((self.docked, self.amr_stopped, self.arm_ready,
                    self.output_clear, self.communication_fresh))

class Lease:
    """Single-process illustrative resource fencing."""
    def __init__(self):
        self.owner = None
        self.epoch = 0

    def acquire(self, owner):
        if not owner or self.owner is not None:
            raise ValueError("BUSY_OR_INVALID")
        self.owner = owner
        self.epoch += 1
        return self.epoch

    def release(self, owner, epoch):
        if self.owner != owner or self.epoch != epoch:
            raise ValueError("STALE_OWNER")
        self.owner = None
