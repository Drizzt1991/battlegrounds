from unittest import TestCase

from engine.geometry import AABB, Circle, Vector


class TestCircle(TestCase):

    def test_circle_eq(self):
        self.assertEqual(Circle(Vector(2, 2), 5), Circle(Vector(2, 2), 5))

    def test_circle_properties(self):
        c = Circle(Vector(2, 2), 5)
        self.assertEqual(c.center, Vector(2, 2))
        self.assertEqual(c.radius, 5)

    def test_circle_contains(self):
        c = Circle(Vector(5, 3), 2)
        self.assertTrue(c.contains(Vector(5, 3)))
        self.assertTrue(c.contains(Vector(5, 1)))
        self.assertFalse(c.contains(Vector(4, 1)))

    def test_circle_distance(self):
        c = Circle(Vector(5, 3), 2)
        self.assertEqual(c.distance(Vector(5, 3)), -1)
        self.assertEqual(c.distance(Vector(5, 1)), 0)
        self.assertEqual(c.distance(Vector(5, 0)), 1)

    def test_circle_circle_intersection(self):
        c = Circle(Vector(5, 3), 2)
        # Full containment
        self.assertTrue(c.intersects(Circle(Vector(5, 3), 1)))
        # Intersection 2 points
        self.assertTrue(c.intersects(Circle(Vector(2, 3), 2)))
        # Intersection 1 point
        self.assertTrue(c.intersects(Circle(Vector(2, 3), 1)))
        # No intersection
        self.assertFalse(c.intersects(Circle(Vector(0, 0), 1)))

    def test_circle_bbox(self):
        c = Circle(Vector(5, 3), 2)
        self.assertEqual(c.bbox(), AABB(Vector(3, 1), Vector(7, 5)))
