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


def _sat_test(poly1, poly2, normal):
    sp = []  # projections of self's vertexes onto line n
    for v in poly1.points:
        sp.append(normal.dot(v))
    op = []  # projections of other's vertexes onto line n
    for v in poly2.points:
        op.append(normal.dot(v))
    if max(op) < min(sp) or min(op) > max(sp):
        return False
    return True


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
        points = self._points
        pivot = points[0]
#   lo and hi, along with pivot, are meant to determine the span of edges
#   that may be facing point other.
        lo = 0
        hi = len(points)
#   The point here is to limit us to the span of a single edge.
#   As long as lo + 1 < hi, there is at least one point between lo and hi;
#   as such, the cycle needs to continue.
        while (lo + 1 < hi):
            mid = (lo + hi) // 2
            ori = orient(pivot, points[mid], other)
#   If point other is located on the line pivot-points[mid], we only need to
#   check if it lies on the segment pivot-points[mid] or outside it.
            if ori == 0:
                min_x = min(points[mid].x, pivot.x)
                min_y = min(points[mid].y, pivot.y)
                max_x = max(points[mid].x, pivot.x)
                max_y = max(points[mid].y, pivot.y)
                return min_x <= other.x <= max_x and min_y <= other.y <= max_y
            elif ori < 0:
                hi = mid
            else:
                lo = mid
        if (lo == 0 or hi == len(points)):
            return False
        if orient(points[lo], points[hi], other) < 0:
            return False
        return True

    def intersects(self, other):
        assert isinstance(other, Polygon)
        # Check our polygon normal's
        points = self._points
        prev_point = points[-1]
        for point in points:
            normal = (point - prev_point).rotate_deg(90)
            if not _sat_test(self, other, normal):
                return None
            prev_point = point

        # Check other polygon's normals
        points = other._points
        prev_point = points[-1]
        for point in points:
            normal = (point - prev_point).rotate_deg(90)
            if not _sat_test(self, other, normal):
                return None
            prev_point = point

        return PolygonIntersection(self, other)
