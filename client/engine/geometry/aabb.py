import math

from .shape import BaseIntersection, BaseShape
from .utils import orient
from .vector import EPSILON, Vector


class AABBIntersection(BaseIntersection):

    def resolve_movement(self, movement):
        c1 = self.other._c - movement  # center before movement
        r = self.other._r
        aabb = self.shape

        # Determine point of impact P on AABB. For that we will find an
        # intersection of a line segment C1C2 against an enlarged AABB by
        # circle radius
        min_big, max_big = aabb.min - Vector(r, r), aabb.max + Vector(r, r)
        aabb_big = AABB(min_big, max_big)
        t = aabb_big.time_of_impact(c1, movement)
        assert t <= 1 and t >= 0
        p = c1 + movement * t

        # If P is in edge Voronoi region, we can just perform simple correction
        # If in vertex - we must direct correction in normal direction
        if p.x <= aabb.max.x and p.x >= aabb.min.x:
            normal = Vector(1, 0)
        elif p.y <= aabb.max.y and p.y >= aabb.min.y:
            normal = Vector(0, 1)
        else:
            # Ok, we are in the Vertex region
            vertex = aabb._closest_point(p)
            vertex_circle = Circle(vertex, r)
            # Compute real time of impact
            t = vertex_circle.time_of_impact(c1, movement)
            assert t <= 1 and t >= 0
            # Compute real point of impact
            p = c1 + movement * t
            s = vertex - p
            # Calculate correction vector
            if orient(Vector(0, 0), s, movement) > 0:
                normal = s.rotate_deg(90)
            else:
                normal = s.rotate_deg(-90)
            normal = normal.unit()

        correction = normal * (normal.dot(movement) * (1 - t))

        return movement * t + correction


class AABB(BaseShape):
    """ Axis Alligned Bounding Box. Rectangle with edges alligned with the
        x and y axes.
    """

    __slots__ = ("_min", "_max")

    def __init__(self, min, max):
        assert isinstance(min, Vector)
        assert isinstance(max, Vector)
        self._min = min
        self._max = max
        super().__init__()

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def center(self):
        return Vector((self._min.x + self._max.x) / 2,
                      (self._min.y + self._max.y) / 2)

    @property
    def width(self):
        return (self._max.x - self._min.x) / 2

    @property
    def height(self):
        return (self._max.y - self._min.y) / 2

    def bbox(self):
        return self

    def __eq__(self, other):
        if isinstance(other, AABB):
            return self._min == other._min and self._max == other._max
        return False

    def __repr__(self):
        return "AABB({}, {})".format(self._min, self._max)

    def contains(self, other):
        assert isinstance(other, Vector)
        if (other.x < self._min.x or other.x > self._max.x or
            other.y < self._min.y or other.y > self._max.y):  # noqa
            return False
        else:
            return True

    def distance2(self, other):
        assert isinstance(other, Vector)
        c = self.center
        w = self.width
        h = self.height
        dx = max(math.fabs(other.x - c.x) - w, 0)
        dy = max(math.fabs(other.y - c.y) - h, 0)
        return dx ** 2 + dy ** 2

    def distance(self, other):
        return math.sqrt(self.distance2(other))

    def intersects(self, other):
        assert isinstance(other, BaseShape)
        if isinstance(other, AABB):
            if (other.min.x > self.max.x or other.min.y > self.max.y):
                return None
            if (other.max.x < self.min.x or other.max.y < self.min.y):
                return None
        if isinstance(other, Circle):
            if (self.distance2(other.center) - other.radius**2 > 0):
                return None
        return AABBIntersection(self, other)

    def time_of_impact(self, point, direction):
        tmin = 0
        tmax = float("inf")
        # Check X slab
        if math.fabs(direction.x) > EPSILON:
            ood = 1.0 / direction.x
            t1 = (self._min.x - point.x) * ood
            t2 = (self._max.x - point.x) * ood
            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > tmin:
                tmin = t1
            if t2 < tmax:
                tmax = t2
            if tmin > tmax:
                return None
        # Check Y slab
        if math.fabs(direction.y) > EPSILON:
            ood = 1.0 / direction.y
            t1 = (self._min.y - point.y) * ood
            t2 = (self._max.y - point.y) * ood
            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > tmin:
                tmin = t1
            if t2 < tmax:
                tmax = t2
            if tmin > tmax:
                return None

        return tmin

    def _closest_point(self, point):
        p_x, p_y = point.x, point.y
        if p_x < self._min.x:
            p_x = self._min.x
        elif p_x > self._max.x:
            p_x = self._max.x
        if p_y < self._min.y:
            p_y = self._min.y
        elif p_y > self._max.y:
            p_y = self._max.y
        return Vector(p_x, p_y)

# Circular import
from .circle import Circle  # noqa
