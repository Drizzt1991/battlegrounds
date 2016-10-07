import math

from .circle import Circle
from .shape import BaseIntersection, BaseShape
from .vector import Vector


class AABBIntersection(BaseIntersection):
    pass


class AABB(BaseShape):

    def __init__(self, min, max):
        assert isinstance(min, Vector)
        assert isinstance(max, Vector)
        self._a = min
        self._b = max

    @property
    def min(self):
        return self._a

    @property
    def max(self):
        return self._b

    def __eq__(self, other):
        if isinstance(other, AABB):
            return self._a == other._a and self._b == other._b

    def contains(self, other):
        assert isinstance(other, Vector)
        if (other.x < self._a.x or other.x > self._b.x or
            other.y < self._a.y or other.y > self._b.y):  # noqa
            return False
        else:
            return True

    def distance2(self, other):
        assert isinstance(other, Vector)
        c = Vector((self._a.x + self._b.x) / 2, (self._a.y + self._b.y) / 2)
        dx = max(abs(other.x - c.x) - (self._b.x - self._a.x) / 2, 0)
        dy = max(abs(other.y - c.y) - (self._b.y - self._a.y) / 2, 0)
        return dx**2 + dy**2

    def distance(self, other):
        return math.sqrt(self.distance2(other))

    def intersects(self, other):
        assert isinstance(other, BaseShape)
        if isinstance(other, AABB):
            if (other.min.x > self.max.x or other.min.y > self.max.y):
                return 0
            if (other.max.x < self.min.x or other.max.y < self.min.y):
                return 0
        if isinstance(other, Circle):
            if (self.distance2(other.center) - other.radius**2 > 0):
                return 0
        return AABBIntersection(self, other)

#        if isinstance(other, Circle):
#            d2 = self._c.distance2(other._c)
#            r2 = (self._r + other._r) ** 2
#            if d2 <= r2:
#                return CircleIntersection(self, other)
