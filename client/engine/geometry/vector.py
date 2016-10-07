import math

EPSILON = 1e-5
EPSILON2 = EPSILON ** 2


def cos_sin_deg(deg):
    """Return the cosine and sin for the given angle
    in degrees, with special-case handling of multiples
    of 90 for perfect right angles
    """
    deg = deg % 360.0
    if deg == 90.0:
        return 0.0, 1.0
    elif deg == 180.0:
        return -1.0, 0
    elif deg == 270.0:
        return 0, -1.0
    rad = math.radians(deg)
    return math.cos(rad), math.sin(rad)


class Vector(object):

    __slots__ = ("_x", "_y")

    def __init__(self, x, y):
        assert isinstance(x, (int, float)), isinstance(y, (int, float))
        self._x = round(float(x), 10)
        self._y = round(float(y), 10)

    @classmethod
    def polar(cls, angle, length=1.0):
        """Create a vector from polar coordinates. Angle should be in radians.
        """
        x, y = math.cos(angle), math.sin(angle)
        return Vector(x * length, y * length)

    @classmethod
    def polar_deg(cls, angle, length=1.0):
        """Create a vector from polar coordinates. Angle should be in degrees.
        """
        return Vector.polar(math.radians(angle), length)

    @property
    def angle(self):
        """The angle the vector makes to the positive x axis in radians
        """
        return math.atan2(self._y, self._x)

    def rotate_deg(self, angle):
        """ Compute a vector, that is rotated by angle deg to this one
        """
        ca, sa = cos_sin_deg(angle)
        return Vector(
            self._x * ca - self._y * sa, self._x * sa + self._y * ca)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __repr__(self):
        return "Vector({}, {})".format(self._x, self._y)

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self._x + other._x, self._y + other._y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self._x - other._x, self._y - other._y)
        return NotImplemented

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self._x * scalar, self._y * scalar)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self._x == other._x and self._y == other._y
        return NotImplemented

    def length2(self):
        """ Squared length is cheaper to compute """
        return self._x ** 2 + self._y ** 2

    def length(self):
        """ ||v|| """
        return math.hypot(self._x, self._y)

    def unit(self):
        """ Return unit vector """
        l = self.length()
        if math.fabs(l - 1) < EPSILON2:
            return self
        return self * (1 / l)

    def dot(self, other):
        """ Return the dot product of 2 vectors. u ' v """
        assert isinstance(other, Vector)
        return self._x * other._x + self._y * other._y

    def distance2(self, other):
        assert isinstance(other, Vector)
        return (self._x - other._x) ** 2 + (self._y - other._y) ** 2

    def distance(self, other):
        assert isinstance(other, Vector)
        return math.hypot(self._x - other._x, self._y - other._y)
