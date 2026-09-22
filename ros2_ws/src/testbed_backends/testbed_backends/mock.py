import math
from .base import Snapshot


class MockMotion:
    """Deterministic straight-line model; no collisions/nav/physics."""

    def __init__(self, x=0.0, y=0.0, speed=1.0):
        if not all(math.isfinite(v) for v in (x, y, speed)) or speed <= 0:
            raise ValueError('finite position and positive finite speed required')
        self.x, self.y, self.speed = float(x), float(y), float(speed)
        self._target = (self.x, self.y)
        self._total = 0.0
        self._progress = 0.0
        self._done = False
        self._active = False

    def start(self, target_x, target_y):
        if not all(math.isfinite(v) for v in (target_x, target_y)):
            raise ValueError('target must be finite')
        self._target = (target_x, target_y)
        self._total = math.hypot(target_x - self.x, target_y - self.y)
        self._done = self._total <= 1e-9
        self._progress = 1.0 if self._done else 0.0
        self._active = not self._done

    def step(self, dt):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError('dt must be finite and nonnegative')
        if self._active:
            dx, dy = self._target[0] - self.x, self._target[1] - self.y
            distance = math.hypot(dx, dy)
            move = min(self.speed * dt, distance)
            if distance > 1e-9:
                self.x += dx / distance * move
                self.y += dy / distance * move
            remaining = math.hypot(self._target[0] - self.x, self._target[1] - self.y)
            self._progress = min(1.0, max(0.0, 1.0 - remaining / self._total))
            if remaining <= 1e-9:
                self.x, self.y = self._target
                self._done, self._active, self._progress = True, False, 1.0
        return self.snapshot()

    def stop(self):
        self._active = False
        self._done = False

    def snapshot(self):
        return Snapshot(self.x, self.y, self._progress, self._done)
