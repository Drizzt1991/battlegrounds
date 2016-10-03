from .shape import BaseIntersection, BaseShape
from .vector import Vector


class CircleIntersection(BaseIntersection):
    pass


class Circle(BaseShape):

    def __init__(self, center, radius):
        assert isinstance(center, Vector)
        assert isinstance(radius, (int, float))
        self._c = center
        self._r = radius

    @property
    def center(self):
        return self._c

    @property
    def radius(self):
        return self._r

    def __eq__(self, other):
        if isinstance(other, Circle):
            return self._r == other._r and self._c == other._c

    def contains(self, other):
        assert isinstance(other, Vector)
        dist2 = other.distance2(self._c)
        r2 = self._r ** self._r
        if dist2 > r2:
            return False
        return True

    def distance(self, other):
        assert isinstance(other, Vector)
        dist = other.distance(self._c)
        if dist >= self._r:
            return dist - self._r
        return -1

    def intersects(self, other):
        assert isinstance(other, BaseShape)
        if isinstance(other, Circle):
            d2 = self._c.distance2(other._c)
            r2 = (self._r + other._r) ** 2
            if d2 <= r2:
                return CircleIntersection(self, other)
