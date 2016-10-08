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
        self._min = min
        self._max = max

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    def __eq__(self, other):
        if isinstance(other, AABB):
            return self._min == other._min and self._max == other._max

    def contains(self, other):
        assert isinstance(other, Vector)
        if (other.x < self._min.x or other.x > self._max.x or
            other.y < self._min.y or other.y > self._max.y):  # noqa
            return False
        else:
            return True

    def distance2(self, other):
        assert isinstance(other, Vector)
        c = Vector((self._min.x + self._max.x) / 2,
                   (self._min.y + self._max.y) / 2)
        dx = max(abs(other.x - c.x) - (self._max.x - self._min.x) / 2, 0)
        dy = max(abs(other.y - c.y) - (self._max.y - self._min.y) / 2, 0)
        return dx**2 + dy**2

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
