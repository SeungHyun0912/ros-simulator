from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Snapshot:
    x: float
    y: float
    progress: float
    done: bool


class MotionBackend(Protocol):
    def start(self, target_x: float, target_y: float) -> None: ...
    def step(self, dt: float) -> Snapshot: ...
    def stop(self) -> None: ...
    def snapshot(self) -> Snapshot: ...
