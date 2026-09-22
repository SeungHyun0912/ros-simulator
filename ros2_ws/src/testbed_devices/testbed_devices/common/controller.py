from testbed_backends.base import MotionBackend


class DeviceController:
    """Single task state machine. Caller owns thread synchronization."""

    def __init__(self, backend: MotionBackend):
        self.backend = backend
        self.status = 'IDLE'
        self.command_id = ''
        self.error_code = ''
        self._seen = set()

    def start(self, command_id, x, y):
        if self.status == 'RUNNING':
            raise ValueError('BUSY')
        if not isinstance(command_id, str) or not command_id.strip():
            raise ValueError('INVALID_ID')
        if command_id in self._seen:
            raise ValueError('DUPLICATE')
        self.backend.start(x, y)
        self._seen.add(command_id)
        self.command_id = command_id
        self.status, self.error_code = 'RUNNING', ''

    def tick(self, dt):
        if self.status == 'RUNNING':
            snap = self.backend.step(dt)
            if snap.done:
                self.status = 'SUCCEEDED'
            return snap
        return self.backend.snapshot()

    def cancel(self):
        if self.status != 'RUNNING':
            return False
        self.backend.stop()
        self.status, self.error_code = 'CANCELED', 'CANCELED'
        return True

    def fail(self, code='INJECTED'):
        if self.status != 'RUNNING':
            return False
        self.backend.stop()
        self.status, self.error_code = 'FAILED', code
        return True
