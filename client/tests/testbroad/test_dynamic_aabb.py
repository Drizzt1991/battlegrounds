from engine.broad import DynamicAABB
from engine.geometry import AABB, Circle, Polygon, Triangle, Vector

import pytest

from .._testutil import ShapeTestCase


class StabObj:

    def __init__(self, shape, position=Vector(0, 0)):
        self.shape = shape
        self.position = position

    def __str__(self):
        return "StabObj({!r})".format(self.shape)


class TestDynamicAABB(ShapeTestCase):

    _shapes = {
        'triangle': Triangle([Vector(0, 0), Vector(1, 0), Vector(1, 1)]),
        'circle': Circle(Vector(0, 0), radius=2),
        'aabb': AABB(Vector(-2, -2), Vector(-1, -1)),
        'poly': Polygon(list(reversed([
            Vector(3, 3), Vector(3.5, 3.5),
            Vector(4.5, 3.5), Vector(4, 3)]))),
    }

    def _create_tree(self):
        tree = DynamicAABB()
        for shape in self._shapes.values():
            tree.add(StabObj(shape), shape.bbox())
        return tree

    def _get_shapes(self, objects):
        return [x.shape for x in objects]

    def _dump_tree(self, node):
        if hasattr(node, '_root'):
            # Actually passed tree object directly
            node = node._root
        result = []
        if node.leaf:
            result.append(node.obj.shape)
        else:
            result.append(self._dump_tree(node.left))
            result.append(self._dump_tree(node.right))
        return result

    @pytest.mark.xfail
    def test_query_shape(self):
        tree = self._create_tree()
        # Check zero results
        r = tree.query_shape(Circle(Vector(5, 5), 1))
        r = self._get_shapes(r)
        self.assertEqual(r, [])
        # Check 1 result
        r = tree.query_shape(Circle(Vector(-2, -2), 0.5))
        r = self._get_shapes(r)
        self.assertEqual(r, [self._shapes['aabb']])
        # Check many results
        r = tree.query_shape(AABB(Vector(-2, -2), Vector(2, 2)))
        r = self._get_shapes(r)
        self.assertEqual(set(r), set([
            self._shapes['aabb'], self._shapes['circle'],
            self._shapes['triangle']]))

    def test_insert_big_and_small(self):
        # This test assures the surface is used in inserts

        # Lets setup a tree with 1 big object and 1 small object.
        tree = DynamicAABB()
        c1 = Circle(Vector(0, 0), 20)
        c2 = Circle(Vector(20, 18), 1)
        tree.add(StabObj(c2), c2.bbox())
        tree.add(StabObj(c1), c1.bbox())
        c3 = Circle(Vector(18, -19), 1)
        tree.add(StabObj(c3), c3.bbox())

        self.assertEqual(self._dump_tree(tree), [
            [[c2], [c3]],
            [c1],
        ])

    def test_remove_one(self):
        tree = DynamicAABB()
        c1 = StabObj(Circle(Vector(0, 0), 1))
        node_id = tree.add(c1, c1.shape.bbox())
        self.assertTrue(tree._root)
        tree.remove(node_id)
        self.assertFalse(tree._root)

    @pytest.mark.xfail
    def test_insert_balanced(self):
        tree = DynamicAABB()
        # By inserting same shape, tree will not balance based on surface
        # checks, so we can check the height balancing
        shape = AABB(Vector(0, 0), Vector(1, 1))
        nodes = []
        for i in range(128):
            nodes.append(tree.add(StabObj(shape), shape.bbox()))

        self.assertEqual(tree.get_height(), 5)
