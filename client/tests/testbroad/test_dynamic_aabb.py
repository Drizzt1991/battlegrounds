import unittest

from engine.broad import DynamicAABB
from engine.geometry import AABB, Circle, Polygon, Triangle, Vector


class StabObj:

    def __init__(self, shape):
        self.shape = shape

    def __eq__(self, other):
        if isinstance(other, StabObj):
            return self.shape == other.shape
        raise NotImplemented

    def __str__(self):
        return "StabObj({!r})".format(self.shape)


class TestDynamicAABB(unittest.TestCase):

    _shapes = {
        'triangle': Triangle([Vector(0, 0), Vector(1, 0), Vector(1, 1)]),
        'circle': Circle(Vector(0, 0), radius=2),
        'aabb': AABB(Vector(-2, -2), Vector(-1, -1)),
        'poly': Polygon([
            Vector(3, 3), Vector(3.5, 3.5),
            Vector(4.5, 3.5), Vector(4, 3)]),
    }

    def setUp(self):
        self.tree = DynamicAABB()
        for shape in self._shapes.values():
            self.tree.add(StabObj(shape))
        self.tree._print_tree()

    def tearDown(self):
        del self.tree

    def _get_shapes(self, objects):
        return [x.shape for x in objects]

    def test_query_shape(self):
        # Check zero results
        r = self.tree.query_shape(Circle(Vector(5, 5), 1))
        r = self._get_shapes(r)
        self.assertEqual(r, [])
        # Check 1 result
        r = self.tree.query_shape(Circle(Vector(-2, -2), 0.5))
        r = self._get_shapes(r)
        self.assertEqual(r, [self._shapes['aabb']])
        # Check many results
        r = self.tree.query_shape(AABB(Vector(-2, -2), Vector(2, 2)))
        r = self._get_shapes(r)
        self.assertEqual(set(r), set([
            self._shapes['aabb'], self._shapes['circle'],
            self._shapes['triangle']]))
