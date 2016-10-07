import unittest

from engine.geometry import Circle
from engine.geometry import Vector
from engine.geometry.aabb import AABB
from engine.geometry.utils import incircle
from engine.geometry.utils import orient


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

    def test_aabb(self):
        a = Vector(2, 2)
        b = Vector(6, 4)
        rect = AABB(a, b)

        self.assertEqual(rect.distance2(Vector(0, 0)), 8)
        self.assertEqual(rect.distance2(a), 0)
        self.assertEqual(rect.distance2(Vector(3, 3)), 0)
        self.assertEqual(rect.distance2(Vector(4, 3)), 0)
        self.assertEqual(rect.distance2(Vector(8, 5)), 5)
        self.assertEqual(rect.distance2(Vector(1, -1)), 10)
        self.assertEqual(rect.distance2(Vector(4, 1)), 1)
        self.assertEqual(rect.distance2(Vector(9, 3)), 9)
        self.assertEqual(rect.distance2(Vector(5, 5)), 1)
        self.assertEqual(rect.distance2(Vector(0, 4)), 4)

        self.assertEqual(rect.distance(Vector(0, 4)), 2)
        self.assertEqual(rect.distance(Vector(9, 3)), 3.0)

        self.assertEqual(rect.contains(a), True)
        self.assertEqual(rect.contains(b), True)
        self.assertEqual(rect.contains(Vector(3, 3)), True)
        self.assertEqual(rect.contains(Vector(-1, -1)), False)
        self.assertEqual(rect.contains(Vector(213132534, -9843574398)), False)

        self.assertEqual(rect.intersects(Circle(Vector(0, 0), 1)), 0)
        self.assertEqual(rect.intersects(Circle(Vector(6, 6.0001), 2)), 0)

        self.assertEqual(rect.intersects(AABB(Vector(0, 0), Vector(1, 2))), 0)
        self.assertEqual(rect.intersects(AABB(Vector(0, 0), Vector(3, 2))), 0)
