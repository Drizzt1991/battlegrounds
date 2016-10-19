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

    def test_distance(self):
        v0 = Vector(8, 5)
        v1 = Vector(5, 7)
        v2 = Vector(2, 6)
        v3 = Vector(2, 5)
        v4 = Vector(3, 2)
        v5 = Vector(5, 1)
        v6 = Vector(7, 1)
        v7 = Vector(9, 3)
        v = Polygon([v0, v1, v2, v3, v4, v5, v6, v7])

        # A point in each Voronoi region of v's AABB
        o0 = Vector(6, -3)
        o1 = Vector(11, -2)
        o2 = Vector(17, -3)
        o3 = Vector(15, 3)
        o4 = Vector(11, 9)
        o5 = Vector(8.5, 9)
        o6 = Vector(-4, 10)
        o7 = Vector(-1, 5)
        o8 = Vector(1, 0)
        o9 = Vector(5, 5)

        # Three points around a vertex (v7), one closest to the vertex,
        # the others closer to its edges.
        o10 = Vector(12, 3)
        o11 = Vector(12, -1)
        o12 = Vector(11, 5)

        # Additional tests for points near the polygon
        o13 = Vector(2, 1)
        o14 = Vector(9, 1)
        o15 = Vector(8, 2)

        # Additional tests for points on or inside the polygon
        o16 = Vector(3, 2)
        o17 = Vector(5.3, 3.09)
        o18 = Vector(6.5, 6)

        self.assertEqual(v.distance(o0), 4)
        self.assertAlmostEqual(v.distance(o1), 4.949747468305833)
        self.assertAlmostEqual(v.distance(o2), 10)
        self.assertAlmostEqual(v.distance(o3), 6)
        self.assertAlmostEqual(v.distance(o4), 5)
        self.assertAlmostEqual(v.distance(o5), 3.605551275463989)
        self.assertAlmostEqual(v.distance(o6), 7.211102550927979)
        self.assertAlmostEqual(v.distance(o7), 3)
        self.assertAlmostEqual(v.distance(o8), 2.82842712474619)
        self.assertEqual(v.distance(o9), -1)

        self.assertEqual(v.distance(o10), 3)
        self.assertAlmostEqual(v.distance(o11), 4.949747468305833)
        self.assertAlmostEqual(v.distance(o12), 2.683281572999748)

        self.assertAlmostEqual(v.distance(o13), 1.414213562373095)
        self.assertAlmostEqual(v.distance(o14), 1.414213562373095)
        self.assertEqual(v.distance(o15), 0)

        self.assertEqual(v.distance(o16), 0)
        self.assertEqual(v.distance(o17), -1)
        self.assertEqual(v.distance(o18), 0)
