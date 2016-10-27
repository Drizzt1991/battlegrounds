import unittest

from engine.geometry import Vector


class TestVector(unittest.TestCase):

    def test_vector_eq(self):
        self.assertEqual(Vector(2, 2), Vector(2, 2))
        self.assertEqual(Vector(0, 0), Vector(0, 0))
        self.assertNotEqual(Vector(2, 1), Vector(1, 2))
        # Low prescision error
        self.assertEqual(
            Vector(0.7071067811865475, 0.7071067811865475),
            Vector(0.7071067811865476, 0.7071067811865475))
        # Wrong types
        self.assertNotEqual(Vector(2, 2), 1)

    def test_vector_add(self):
        u = Vector(2, 1)
        v = Vector(0, 1)
        self.assertEqual(u + v, Vector(2, 2))
        self.assertEqual(v + u, Vector(2, 2))

        with self.assertRaises(TypeError):
            u + 1

    def test_vector_sub(self):
        u = Vector(2, 5)
        v = Vector(1, 2)
        self.assertEqual(u - v, Vector(1, 3))
        self.assertEqual(v - u, Vector(-1, -3))

        with self.assertRaises(TypeError):
            u - 1

    def test_vector_mul(self):
        u = Vector(2, 5)
        self.assertEqual(u * 2, Vector(4, 10))
        u = Vector(1, 3)
        self.assertEqual(u * 3, Vector(3, 9))

        with self.assertRaises(TypeError):
            u * u

    def test_vector_length(self):
        self.assertEqual(Vector(0, 2.14).length(), 2.14)
        self.assertEqual(Vector(3, 4).length(), 5)

    def test_vector_length2(self):
        self.assertEqual(Vector(0, 2.5).length2(), 6.25)
        self.assertEqual(Vector(3, 4).length2(), 25)

    def test_vector_dot(self):
        u = Vector(2, 5)
        v = Vector(3, 7)
        self.assertEqual(u.dot(v), 41)
        self.assertEqual(v.dot(u), 41)

    def test_vector_distance(self):
        self.assertEqual(Vector(0, 3).distance(Vector(0, 4)), 1)
        self.assertEqual(Vector(0, 3).distance(Vector(4, 0)), 5)

    def test_vector_distance2(self):
        self.assertEqual(Vector(0, 3).distance2(Vector(0, 4)), 1)
        self.assertEqual(Vector(0, 3).distance2(Vector(4, 0)), 25)

    def test_vector_unit(self):
        self.assertEqual(Vector(0, 2).unit(), Vector(0, 1))
        self.assertEqual(Vector(0, 1).unit(), Vector(0, 1))
        self.assertEqual(Vector(1, 1).unit(), Vector.polar_deg(45))

    def test_vector_x_y(self):
        u = Vector(4, 3)
        self.assertEqual(u.x, 4)
        self.assertEqual(u.y, 3)
        u = Vector(3.4, 7.8)
        self.assertEqual(u.x, 3.4)
        self.assertEqual(u.y, 7.8)

    def test_vector__str__(self):
        str(Vector(2, 1)) == "Vector(2, 1)"

    def test_vector__repr__(self):
        repr(Vector(2, 1)) == "Vector(2, 1)"
