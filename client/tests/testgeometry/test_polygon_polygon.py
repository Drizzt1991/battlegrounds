import unittest

from engine.geometry.polygon import Polygon
from engine.geometry import Vector


class TestPolygon(unittest.TestCase):

    def test_contains(self):
        v0 = Vector(2, 1)
        v1 = Vector(4, 1)
        v2 = Vector(7, 2)
        v3 = Vector(8, 3)
        v4 = Vector(7, 6)
        v5 = Vector(6, 6)
        v6 = Vector(4, 5)
        v7 = Vector(1, 3)
        v = Polygon([v0, v1, v2, v3, v4, v5, v6, v7])

        self.assertEqual(v.contains(Vector(6, 3)), True)
        self.assertEqual(v.contains(Vector(2, 6)), False)
        self.assertEqual(v.contains(Vector(0, 1)), False)
        self.assertEqual(v.contains(Vector(4, 3)), True)
        self.assertEqual(v.contains(Vector(1, 0)), False)
        self.assertEqual(v.contains(Vector(3, 1)), True)
        self.assertEqual(v.contains(v7), True)
        self.assertEqual(v.contains(Vector(1.5, 2)), True)
        self.assertEqual(v.contains(Vector(605324, 3)), False)
        self.assertEqual(v.contains(v0), True)

    def test_intersects(self):
        v0 = Vector(6, 2)
        v1 = Vector(7, 4)
        v2 = Vector(7, 5)
        v3 = Vector(4, 6)
        v4 = Vector(2, 5)
        v5 = Vector(0, 3)
        v6 = Vector(1, 2)
        v7 = Vector(4, 1)
        v = Polygon([v0, v1, v2, v3, v4, v5, v6, v7])

        o0 = Vector(8, -3)
        o1 = Vector(8, -1)
        o2 = Vector(5, -1)
        o3 = Vector(5, -3)
        other = Polygon([o0, o1, o2, o3])

        o20 = Vector(2, -1)
        o21 = Vector(2, 1)
        o22 = Vector(-2, 5)
        o23 = Vector(-3, -2)
        other2 = Polygon([o20, o21, o22, o23])

        self.assertEqual(v.intersects(other), None)
        self.assertTrue(v.intersects(other2))
        self.assertEqual(other.intersects(other2), None)
