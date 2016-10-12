import unittest

from engine.geometry import Vector
from engine.geometry.polygon import Triangle, classify_polygon, AABB


class TestPolygon(unittest.TestCase):

    def test_classfify_polygon(self):
        # Test Triangle
        p = classify_polygon([Vector(0, 0), Vector(1, 1), Vector(1, 5)])
        self.assertIsInstance(p, Triangle)
        p = classify_polygon([Vector(0, 0), Vector(1, 5), Vector(1, 1)])
        self.assertIsInstance(p, Triangle)
        p = classify_polygon([Vector(1, 5), Vector(0, 0), Vector(1, 1)])
        self.assertIsInstance(p, Triangle)
        p = classify_polygon([
            Vector(0.4, 0.8), Vector(3.4, 1.2), Vector(5.6, 0.4)])
        self.assertIsInstance(p, Triangle)

        # Test AABB
        p = classify_polygon([
            Vector(0, 0), Vector(1, 0), Vector(1, 1), Vector(0, 1)])
        self.assertIsInstance(p, AABB)
        p = classify_polygon([
            Vector(1, 0), Vector(1, 1), Vector(0, 1), Vector(0, 0)])
        self.assertIsInstance(p, AABB)
        p = classify_polygon([
            Vector(1, 1), Vector(0, 1), Vector(0, 0), Vector(1, 0)])
        self.assertIsInstance(p, AABB)

        with self.assertRaises(NotImplementedError):
            classify_polygon([
                Vector(1, 1), Vector(0, 0), Vector(0, 1), Vector(1, 0)])
