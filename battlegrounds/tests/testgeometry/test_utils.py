import unittest

from engine.geometry import Vector
from engine.geometry.utils import incircle, orient, seg_distance


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

    def test_seg_distance(self):
        # An easily visualized test involving a segment parallel to the X axis
        a1 = Vector(-2, 1)
        b1 = Vector(4, 1)
        c1 = Vector(0, 6)
        c2 = Vector(7, 5)
        # Points in close proximity to the segment for high precision checks
        c3 = Vector(-2.01, 1)
        c4 = Vector(0, 0.999999998)
        c5 = Vector(4.0000000001, 0.99999999998)
        self.assertEqual(seg_distance(a1, b1, c1), 5)
        self.assertEqual(seg_distance(a1, b1, c2), 5)
        self.assertAlmostEqual(seg_distance(a1, b1, c3), 0.01)
        self.assertAlmostEqual(seg_distance(a1, b1, c4), 0.000000002)
        self.assertGreater(seg_distance(a1, b1, c5), 0)
