import unittest

from engine.geometry import Vector
from engine.geometry.polygon import Triangle


class TestTriangle(unittest.TestCase):

    def test_triangle_contains(self):
        t = Triangle([Vector(2, 2), Vector(4, 4), Vector(4, 2)])
        # Inside triangle
        self.assertTrue(t.contains(Vector(3.5, 3)))
        # On edge
        self.assertTrue(t.contains(Vector(3, 2)))
        # Exactly vertex
        self.assertTrue(t.contains(Vector(2, 2)))
        # Outside
        self.assertFalse(t.contains(Vector(2, 1)))

    def test_triangle_distance(self):
        t = Triangle([Vector(2, 2), Vector(4, 4), Vector(4, 2)])
        # Inside triangle
        self.assertEqual(t.distance(Vector(3.5, 3)), -1)
        # On edge
        self.assertEqual(t.distance(Vector(3, 2)), 0)
        # Exactly vertex
        self.assertEqual(t.distance(Vector(2, 2)), 0)
        # Outside in a vertex voronoi region
        self.assertEqual(t.distance(Vector(-2, -1)), 5)
        # Outside in a edge voronnoi region
        self.assertEqual(t.distance(Vector(3, 0)), 2)
