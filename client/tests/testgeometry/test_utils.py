import unittest

from engine.geometry import Vector
from engine.geometry.utils import orient
from engine.geometry.utils import incircle


class TestUtils(unittest.TestCase):

    def test_orient(self):
        a = Vector(0, 0)
        b = Vector(1, 1)
        self.assertGreater(orient(a, b, Vector(0, 1)), 0)
        self.assertLess(orient(a, b, Vector(1, 0)), 0)
        self.assertEqual(orient(a, b, Vector(5, 5)), 0)
        self.assertLess(orient(a, b, Vector(.745, .0005)), 0)
        self.assertLess(orient(Vector(0, 1), Vector(11, -2), Vector(1, -4)), 0)
        a2 = Vector(0.0000003, 0.0000006)
        b2 = Vector(0.000000301001, 0.0000006)
        self.assertGreater(orient(a2, b2, Vector(5, 5)), 0)

    def test_incircle(self):
        a = Vector(0, 0)
        b = Vector(2, 0)
        c = Vector(1, 1)
        self.assertGreater(incircle(a, b, c, Vector(1, 0)), 0)
        self.assertGreater(incircle(a, b, c, Vector(1, 0.9999999991999)), 0)
        self.assertLess(incircle(a, b, c, Vector(-11, 0)), 0)
        self.assertEqual(incircle(a, b, c, Vector(1, 1)), 0)
        self.assertEqual(incircle(a, b, c, Vector(1, -1)), 0)
