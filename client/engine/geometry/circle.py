import math

from .shape import BaseIntersection, BaseShape
from .utils import orient
from .vector import Vector


class CircleIntersection(BaseIntersection):

    def __init__(self, shape, other):
        self.shape = shape
        self.other = other

    def resolve_movement(self, movement):
        # Change the task to movement of point against a bigger circle
        initial_center = self.other._c - movement
        s = initial_center - self.shape._c
        r = self.other._r + self.shape._r
        v = movement
        c = s.dot(s) - r * r
        if c > 0:
            # Compute the determinant for movement equation
            # (v · v)t2 + 2(v · s)t + (s · s − r ^ 2) = 0
            a = v.dot(v)
            b = v.dot(s)
            d = b * b - a * c
            time_of_contact = (-b - math.sqrt(d)) / a
            assert time_of_contact > 0 and time_of_contact <= 1
        else:
            # Circle was intersecting before movement
            time_of_contact = 0
        processed = movement * time_of_contact
        # correction_len = movement.length() * (1 - time_of_contact)

        # Calculate correction vector
        if orient(Vector(0, 0), s, movement) > 0:
            normal = s.rotate_deg(90)
        else:
            normal = s.rotate_deg(-90)
        normal = normal.unit()
        correction = normal * (normal.dot(movement) * (1 - time_of_contact))
        return processed + correction


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

    def bbox(self):
        c = self._c
        r = self._r
        min_x, min_y = c.x - r, c.y - r
        max_x, max_y = c.x + r, c.y + r
        return AABB(Vector(min_x, min_y), Vector(max_x, max_y))

    def __eq__(self, other):
        if isinstance(other, Circle):
            return self._r == other._r and self._c == other._c
        return False

    def __repr__(self):
        return "Circle({}, {})".format(self._c, self._r)

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

    def time_of_impact(self, point, direction):
        m = point - self._c
        b = m.dot(direction)
        c = m.dot(m) - self._r ** 2
        # Fast exit if point outside of circle and direction points away too
        if c > 0 and b > 0:
            return None
        # Next we solve an equation t^2 +2(m·d)t+(m·m)−r2 = 0
        discr = b * b - c
        # A negative discriminant corresponds to ray missing sphere
        if discr < 0:
            return None
        # Ray now found to intersect sphere, compute smallest t value of
        # intersection
        t = -b - math.sqrt(discr)
        # If t is negative, ray started inside sphere so clamp t to zero
        if t < 0:
            t = 0
        return t

    def translate(self, position):
        return Circle(self._c + position, self._r)


# Circular import
from .aabb import AABB  # noqa
