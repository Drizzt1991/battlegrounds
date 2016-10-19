import unittest

from engine.geometry import AABB, Circle, Triangle, Vector


class TestAABB(unittest.TestCase):

    def test_dist(self):
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

    def test_contains(self):
        a = Vector(2, 2)
        b = Vector(6, 4)
        rect = AABB(a, b)

        self.assertEqual(rect.contains(a), True)
        self.assertEqual(rect.contains(b), True)
        self.assertEqual(rect.contains(Vector(3, 3)), True)
        self.assertEqual(rect.contains(Vector(-1, -1)), False)
        self.assertEqual(rect.contains(Vector(213132534, -9843574398)), False)

    def test_intersects_circle(self):
        rect = AABB(Vector(2, 2), Vector(6, 4))
        zr = Vector(0, 0)
        self.assertEqual(rect.intersects(Circle(zr, 1)), None)
        self.assertEqual(rect.intersects(Circle(Vector(6, 6.0001), 2)), None)

    def test_intersects_aabb(self):
        rect = AABB(Vector(2, 2), Vector(6, 4))
        zr = Vector(0, 0)
        self.assertEqual(rect.intersects(AABB(zr, Vector(1, 2))), None)
        self.assertTrue(rect.intersects(AABB(zr, Vector(3, 2))))

    def test_intersects_triangle(self):
        rect = AABB(Vector(-2, -2), Vector(2, 2))
        # Outside, separated by AC's normal
        t = Triangle([Vector(2, 3), Vector(3, 2), Vector(3, 3)])
        self.assertFalse(rect.intersects(t))
        # Outside, separated by X axis
        t = Triangle([Vector(-1, 3), Vector(0, 2.1), Vector(1, 3)])
        self.assertFalse(rect.intersects(t))
        # On border
        t = Triangle([Vector(2, 3), Vector(2, 2), Vector(3, 2)])
        self.assertTrue(rect.intersects(t))
        # Overlap
        t = Triangle([Vector(3, 0), Vector(3, 3), Vector(0, 3)])
        self.assertTrue(rect.intersects(t))

    def test_bbox(self):
        rect = AABB(Vector(2, 2), Vector(6, 4))
        self.assertEqual(rect, rect.bbox())
