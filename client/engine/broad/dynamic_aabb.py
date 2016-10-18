# Source http://www.randygaul.net/2013/08/06/dynamic-aabb-tree/
from engine.geometry.shape import BaseShape

from .abc import ABCBroadPhase


class Node(object):

    leaf = False

    def __init__(self, *, left, right, parent, aabb):
        self.left = left
        self.right = right
        self.parent = parent
        self.aabb = aabb

    def __repr__(self):
        return "Node({})".format(self.aabb)


class LeafNode(object):

    leaf = True
    parent = None

    def __init__(self, *, obj, aabb):
        self.obj = obj
        self.aabb = aabb

    def __repr__(self):
        return "LeafNode({}, {})".format(self.obj, self.aabb)


class DynamicAABB(ABCBroadPhase):

    def __init__(self):
        self._root = None

    def add(self, obj):
        if not hasattr(obj, "shape") or not isinstance(obj.shape, BaseShape):
            raise ValueError(obj)

        leaf_node = LeafNode(obj=obj, aabb=obj.shape.bbox())
        node = self._root
        # First insertion case
        if node is None:
            self._root = leaf_node
            return
        shape_aabb = leaf_node.aabb

        # Find which node to append to
        while not node.leaf:
            insert_to = self._insert_strategy(node, shape_aabb)
            if insert_to is None:  # Node found
                break
            node = insert_to

        old_parent = node.parent
        new_parent = Node(
            left=node, right=leaf_node, parent=old_parent,
            aabb=node.aabb.union(shape_aabb))

        # Link nodes togather
        node.parent = new_parent
        leaf_node.parent = new_parent
        if old_parent is None:
            self._root = new_parent
        else:
            if old_parent.left is node:
                old_parent.left = new_parent
            else:
                old_parent.right = new_parent

            # Traverse up the tree and fix other aabb's
            parent = old_parent
            while parent is not None:
                new_aabb = parent.aabb.union(shape_aabb)
                if parent.aabb == new_aabb:
                    break
                parent.aabb = new_aabb

    def _insert_strategy(self, node, aabb):
        """ For each node we can do one of the 3 cases for insertion:
                * insert to right branch recurcively
                * insert to left branch recurcively
                * add it to current node
            Returns node to proceed recurcively on or None to indicate
            insertion to this node

            Ref: Formulas are descibed in detail in "Real Time Collision
            Detection" book, but implementation took from here:
            https://github.com/azrafe7/hxAABBTree
        """
        left = node.left
        right = node.right

        area = node.aabb.area()
        combined_area = node.aabb.union(aabb).area()
        # Cost of creating a new node instead of this one
        cost_parent = 2 * area
        # Minimum cost of pushing the leaf further down the tree
        cost_descend = 2 * (combined_area - area)

        # cost of descending into left node
        cost_left = left.aabb.union(aabb).area() + cost_descend
        if not left.leaf:
            cost_left -= left.aabb.area()

        # cost of descending into right node
        cost_right = right.aabb.union(aabb).area() + cost_descend
        if not right.leaf:
            cost_right -= right.aabb.area()

        if cost_left < cost_parent and cost_right < cost_parent:
            return None
        elif cost_left < cost_right:
            return left
        else:
            return right

    def query_shape(self, shape):
        if not isinstance(shape, BaseShape):
            raise ValueError(shape)

        shape_aabb = shape.bbox()
        results = []
        for obj in self._query_aabb(self._root, shape_aabb):
            print(obj)
            if obj.shape.intersects(shape):
                results.append(obj)
        return results

    def _query_aabb(self, node, aabb):
        if node is None or not node.aabb.intersects(aabb):
            return
        if node.leaf:
            yield node.obj
        else:
            yield from self._query_aabb(node.right, aabb)
            yield from self._query_aabb(node.left, aabb)

    def _print_tree(self, node=None, indent=0):
        if node is None:
            node = self._root
        print(" " * indent + str(node))
        if not node.leaf:
            self._print_tree(node.left, indent=indent + 2)
            self._print_tree(node.right, indent=indent + 2)
