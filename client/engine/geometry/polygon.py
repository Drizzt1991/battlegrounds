from .shape import BaseIntersection, BaseShape
from .utils import orient
from .vector import Vector


class TriangleIntersection(BaseIntersection):
    pass


class Triangle(BaseShape):

    def __init__(self, points):
        assert len(points) == 3
        assert orient(*points) < 0
        self._a, self._b, self._c = points

    @property
    def points(self):
        return (self._a, self._b, self._c)

    def contains(self, other):
        assert isinstance(other, Vector)
        a, b, c = self._a, self._b, self._c
        if orient(a, b, other) > 0:
            return False
        if orient(b, c, other) > 0:
            return False
        if orient(c, a, other) > 0:
            return False
        return True

    def _closest_point(self, p):
        """ Taken from "Real-Time Collision Detection" book.
            http://realtimecollisiondetection.net/
        """
        a, b, c = self._a, self._b, self._c
        ab = b - a
        ac = c - a
        ap = p - a
        d1 = ab.dot(ap)
        d2 = ac.dot(ap)
        # d1 and d2 are projections of AP onto AB and AC. If they both are less
        # then 0, than P is in A's voronoi region and so A is the closest point
        if d1 <= 0 and d2 <= 0:
            return a

        # Check if P is in B vertex voronoi region
        bp = p - b
        d3 = ab.dot(bp)
        d4 = ac.dot(bp)
        if d3 >= 0 and d4 <= d3:
            return b

        # Check if P is in AB edge voronoi region
        vc = d1 * d4 - d3 * d2
        if vc <= 0 and d1 >= 0 and d3 <= 0:
            w = d1 / (d1 - d3)
            return a + w * ab

        # Check if P in vertex region of C
        cp = p - c
        d5 = ab.dot(cp)
        d6 = ac.dot(cp)
        # Same as for B
        if d6 >= 0 and d5 <= d6:
            return c

        # Check if P in edge region of AC
        vb = d5 * d2 - d1 * d6
        if vb <= 0 and d2 >= 0 and d6 <= 0:
            w = d2 / (d2 - d6)
            return a + w * ac

        # Ckeck if P is in edge region of BC
        va = d3 * d6 - d5 * d4
        if va <= 0 and (d4 - d3) >= 0 and (d5 - d6) >= 0:
            w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
            return b + w * (c - b)

        # P inside of the triangle
        return p

    def distance(self, other):
        assert isinstance(other, Vector)
        x = self._closest_point(other)
        if other is x:
            return -1
        return x.distance(other)


class PolygonIntersection(BaseIntersection):
    pass


class Polygon(BaseShape):
    """(Assuming that the polygon is convex and ordered counter-clockwise)"""

    def __init__(self, points):
        assert len(points) >= 3
        self._points = points

    @property
    def points(self):
        return self._points

    def contains(self, other):
        assert isinstance(other, Vector)
        lo = 0
        hi = len(self.points)
        while (lo + 1 < hi):
            mid = (lo + hi) // 2
            if orient(self.points[0], self.points[mid], other) == 0:
                lx = abs(other.x - self.points[0].x)
                lx += abs(self.points[mid].x - other.x)
                ly = abs(other.y - self.points[0].y)
                ly += abs(self.points[mid].y - other.y)
                if (abs(self.points[mid].x - self.points[0].x) == lx and
                    abs(self.points[mid].y - self.points[0].y) == ly):  # noqa
                    return True
                else:
                    return False
            elif orient(self.points[0], self.points[mid], other) < 0:
                hi = mid
            else:
                lo = mid
        if (lo == 0 or hi == len(self.points)):
            return False
        if orient(self.points[lo], self.points[hi], other) < 0:
            return False
        return True

    def intersects(self, other):
        assert isinstance(other, Polygon)
        ns = []  # list of normals to each edge of both polygons
        for i in range(0, len(self.points) - 1):
            ns.append(Vector(self.points[i + 1].y - self.points[i].y,
                             self.points[i].x - self.points[i + 1].x))
        ns.append(Vector(self.points[i].y - self.points[0].y,
                         self.points[0].x - self.points[i].x))
        for i in range(0, len(other.points) - 1):
            ns.append(Vector(other.points[i + 1].y - other.points[i].y,
                             other.points[i].x - other.points[i + 1].x))
        ns.append(Vector(other.points[i].y - other.points[0].y,
                         other.points[0].x - other.points[i].x))
        for n in ns:
            sp = []  # projections of self's vertexes onto line n
            for v in self.points:
                sp.append(v.dot(n))
            op = []  # projections of other's vertexes onto line n
            for v in other.points:
                op.append(v.dot(n))
            if max(op) < min(sp) or min(op) > max(sp):
                return None
        return PolygonIntersection(self, other)
