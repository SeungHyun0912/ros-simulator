import math
import unittest
from testbed_backends.mock import MockMotion
from testbed_backends.isaac import IsaacMotion
from testbed_devices.common.controller import DeviceController


class BackendTests(unittest.TestCase):
    def test_arrival(self):
        m = MockMotion(speed=1.0)
        m.start(3.0, 4.0)
        s = m.step(5.0)
        self.assertTrue(s.done)
        self.assertAlmostEqual(s.x, 3.0)
        self.assertAlmostEqual(s.y, 4.0)

    def test_intermediate(self):
        m = MockMotion(speed=2.0)
        m.start(10.0, 0.0)
        s = m.step(1.0)
        self.assertAlmostEqual(s.progress, 0.2)
        self.assertAlmostEqual(s.x, 2.0)
        self.assertFalse(s.done)

    def test_no_overshoot(self):
        m = MockMotion()
        m.start(1.0, 0.0)
        self.assertEqual(m.step(100.0).x, 1.0)

    def test_zero_distance(self):
        m = MockMotion()
        m.start(0.0, 0.0)
        self.assertTrue(m.step(0.0).done)

    def test_stop(self):
        m = MockMotion()
        m.start(10.0, 0.0)
        m.step(1.0)
        m.stop()
        s = m.step(100.0)
        self.assertEqual(s.x, 1.0)
        self.assertFalse(s.done)

    def test_invalid_speed(self):
        for value in (0.0, -1.0, math.nan, math.inf):
            with self.assertRaises(ValueError):
                MockMotion(speed=value)

    def test_invalid_target(self):
        with self.assertRaises(ValueError):
            MockMotion().start(math.nan, 0.0)

    def test_invalid_dt(self):
        for dt in (-1.0, math.nan, math.inf):
            with self.assertRaises(ValueError):
                MockMotion().step(dt)

    def test_isaac_fail_fast(self):
        with self.assertRaises(NotImplementedError):
            IsaacMotion()


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.c = DeviceController(MockMotion())

    def test_success(self):
        self.c.start('a', 1.0, 0.0)
        self.assertEqual(self.c.status, 'RUNNING')
        self.c.tick(1.0)
        self.assertEqual(self.c.status, 'SUCCEEDED')

    def test_busy(self):
        self.c.start('a', 10.0, 0.0)
        with self.assertRaisesRegex(ValueError, 'BUSY'):
            self.c.start('b', 1.0, 0.0)

    def test_duplicate(self):
        self.c.start('a', 1.0, 0.0)
        self.c.tick(1.0)
        with self.assertRaisesRegex(ValueError, 'DUPLICATE'):
            self.c.start('a', 2.0, 0.0)

    def test_blank_id(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_ID'):
            self.c.start(' ', 1.0, 0.0)

    def test_cancel(self):
        self.c.start('a', 10.0, 0.0)
        self.c.tick(1.0)
        self.assertTrue(self.c.cancel())
        self.c.tick(100.0)
        self.assertEqual(self.c.status, 'CANCELED')
        self.assertEqual(self.c.backend.snapshot().x, 1.0)

    def test_idle_cancel(self):
        self.assertFalse(self.c.cancel())

    def test_fault_then_new_command(self):
        self.c.start('a', 10.0, 0.0)
        self.assertTrue(self.c.fail())
        self.assertEqual(self.c.status, 'FAILED')
        self.c.start('b', 1.0, 0.0)
        self.c.tick(1.0)
        self.assertEqual(self.c.status, 'SUCCEEDED')


if __name__ == '__main__':
    unittest.main()
