"""
    Basic concept described here:

        http://www.randygaul.net/2013/08/06/dynamic-aabb-tree/

    Other refs:
        Formulas of how to insert/remove nodes are descibed in detail in
        "Real Time Collision Detection" book, which has refs for further
        reading on the topic
        Implementation was more/less taken from here:

            https://github.com/azrafe7/hxAABBTree

        which is basically a more readable version of Box2d's implementation:

            https://github.com/erincatto/Box2D/blob/master/Box2D/Box2D/Collision/b2DynamicTree.cpp


// Separating axis for segment (Gino, p80).
        // |dot(v, p1 - c)| > dot(|v|, h)
        b2Vec2 c = node->aabb.GetCenter();
        b2Vec2 h = node->aabb.GetExtents();
        float32 separation = b2Abs(b2Dot(v, p1 - c)) - b2Dot(abs_v, h);
        if (separation > 0.0f)
        {
            continue;
        }

"""


from engine.geometry.shapes.shape import BaseShape

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

    def __init__(self, *, node_id, obj, aabb):
        self.obj = obj
        self.aabb = aabb
        self.node_id = node_id

    def __repr__(self):
        return "LeafNode({}, {})".format(self.obj, self.aabb)


class DynamicAABB(ABCBroadPhase):

    def __init__(self):
        self._root = None
        self._leaves = {}  # Leaves only
        self._next_id = 0  # Next leaf ID

    def add(self, obj, shape_aabb):
        leaf_node = LeafNode(
            node_id=self._next_id, obj=obj, aabb=shape_aabb)
        self._next_id += 1
        self._leaves[leaf_node.node_id] = leaf_node
        node = self._root
        # First insertion case
        if node is None:
            self._root = leaf_node
            return leaf_node.node_id

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
            current = old_parent
            while current is not None:
                new_aabb = current.aabb.union(shape_aabb)
                if current.aabb == new_aabb:
                    break
                current.aabb = new_aabb
                current = current.parent
        return leaf_node.node_id

    def remove(self, node_id):
        node = self._leaves.pop(node_id, None)
        if node is None:
            raise KeyError(node_id)
        parent = node.parent
        # Check if it's last (root) node
        if parent is None:
            self._root = None
            return

        # Remove parent node, as not needed anymore
        grand_parent = parent.parent
        if node is parent.left:
            sibling = parent.right
        else:
            sibling = parent.left
        # If parent's parent is root - just place sibling there
        if grand_parent is None:
            self._root = sibling
            sibling.parent = None
            return
        # Link grand_parent and sibling
        if grand_parent.left is parent:
            grand_parent.left = sibling
        else:
            grand_parent.right = sibling
        sibling.parent = grand_parent

        # Adjust all nodes up the tree
        current = grand_parent
        while current is not None:
            new_aabb = current.left.aabb.union(current.right.aabb)
            if current.aabb == new_aabb:
                break
            current.aabb = new_aabb
            current = current.parent

        # Unlink node for easier GC
        node.parent = None

    def _insert_strategy(self, node, aabb):
        """ For each node we can do one of the 3 cases for insertion:
                * insert to right branch recurcively
                * insert to left branch recurcively
                * add it to current node
            Returns node to proceed recurcively on or None to indicate
            insertion to this node
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

        if cost_left >= cost_parent and cost_right >= cost_parent:
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

    def get_height(self, node=None):
        if node is None:
            node = self._root
        if node.leaf:
            return 1
        else:
            h = max(self.get_height(node.left), self.get_height(node.right))
            return h + 1
