from .aabb import AABB
from .circle import Circle
from .shape import BaseIntersection, BaseShape
from .utils import orient, seg_distance
from .vector import Vector


def classify_polygon(points):
    """ Factory for polygons, will analyze points and return an instance of
        this polygon
    """
    if len(points) == 3:
        if orient(*points) > 0:
            points.reverse()
        return Triangle(points)
    if len(points) == 4:
        # TEST AABB
        a, b, c, d = sorted(points, key=lambda k: (k.x, k.y))
        if a.x == b.x and c.x == d.x and a.y == c.y and b.y == d.y:
            # Check for ribbon case
            if (points.index(a) - points.index(d)) % 2 == 0:
                return AABB(a, d)
    raise NotImplementedError()


class TriangleIntersection(BaseIntersection):

    def __init__(self, shape, other, closest):
        self.shape = shape
        self.other = other
        self._closest = closest

    def resolve_movement(self, movement):
        force = self._closest - self.other.center
        d = force.length()
        penetration = self.other.radius - d
        correction = penetration * force.unit()
        return movement - correction


class Triangle(BaseShape):

    def __init__(self, points):
        assert len(points) == 3
        assert orient(*points) < 0
        self._a, self._b, self._c = points

    def __eq__(self, other):
        if isinstance(other, Triangle):
            return self._a == other._a and self._b == other._b and \
                self._c == other._c
        raise NotImplemented

    def __hash__(self):
        return hash((self.__class__, self._a, self._b, self._c))

    def __repr__(self):
        return "Triangle({})".format(list(self.points))

    def bbox(self):
        a, b, c = self._a, self._b, self._c
        min_x, min_y = min(a.x, b.x, c.x), min(a.y, b.y, c.y)
        max_x, max_y = max(a.x, b.x, c.x), max(a.y, b.y, c.y)
        return AABB(Vector(min_x, min_y), Vector(max_x, max_y))

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

    def intersects(self, other):
        if isinstance(other, Circle):
            closest = self._closest_point(other.center)
            if ((closest.distance2(other.center) - other.radius ** 2) < 0):
                return TriangleIntersection(self, other, closest)


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
        self._points = tuple(points)

    def __eq__(self, other):
        if isinstance(other, Polygon):
            return self._points == other._points
        raise NotImplemented

    def __hash__(self):
        return hash((self.__class__, self._points))

    def __repr__(self):
        return "Polygon({})".format(list(self.points))

    def bbox(self):
        axis = [p.x for p in self._points]
        min_x = min(axis)
        max_x = max(axis)
        axis = [p.y for p in self._points]
        min_y = min(axis)
        max_y = max(axis)
        return AABB(Vector(min_x, min_y), Vector(max_x, max_y))

    @property
    def points(self):
        return self._points

    def _contains(self, other):
        assert isinstance(other, Vector)
        points = self._points
        pivot = points[0]
        # lo and hi, along with pivot, are meant to determine the span of
        # edges that may be facing point other.
        lo = 0
        hi = len(points)
        # The point here is to limit us to the span of a single edge.
        # As long as lo + 1 < hi, there is at least one point between lo
        # and hi; as such, the cycle needs to continue.
        while (lo + 1 < hi):
            mid = (lo + hi) // 2
            ori = orient(pivot, points[mid], other)
            # If point other is located on the line pivot-points[mid],
            # we only need to check if it lies on the segment
            # pivot-points[mid] or outside it.
            if ori == 0:
                if seg_distance(pivot, points[mid], other) > 0:
                    return -1
                elif mid == 1 or mid == len(points) - 1:
                    return 0
                elif other == pivot or other == points[mid]:
                    return 0
                else:
                    return 1

            elif ori < 0:
                hi = mid
            else:
                lo = mid
        # distance method requires information of whether the point lies on
        # the border or strictly inside the polygon so immediately returning
        # True/False is not an option.
        # A negative return value denotes that the point is outside the polygon
        if (lo == 0 or hi == len(points)):
            return -1
        return orient(points[lo], points[hi], other)

    def contains(self, other):
        if self._contains(other) < 0:
            return False
        else:
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

    def distance(self, other):
        assert isinstance(other, Vector)
        points = self._points
        le = len(points)
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0
        for i in range(1, le):
            if points[min_x].x > points[i].x:
                min_x = i
            if points[max_x].x < points[i].x:
                max_x = i
            if points[min_y].y > points[i].y:
                min_y = i
            if points[max_y].y < points[i].y:
                max_y = i
        # Determining which Voronoi region of the AABB encasing the polygon
        # the point of interest is located in to better choose the pivot point.
        if other.x < points[min_x].x:
            if other.y < points[min_y].y:
                # Point is to the left and below the polygon in the coordinate
                # system
                if min_x > min_y:
                    pivot = (min_x - le + min_y) // 2
                else:
                    pivot = (min_x + min_y) // 2
            elif other.y > points[max_y].y:
                # to the left and above
                if max_y > min_x:
                    pivot = (max_y - le + min_x) // 2
                else:
                    pivot = (max_y + min_x) // 2
            else:
                # straight to the left
                pivot = min_x
        elif other.x > points[max_x].x:
            if other.y < points[min_y].y:
                # to the right and below
                if min_y > max_x:
                    pivot = (min_y - le + max_x) // 2
                else:
                    pivot = (min_y + max_x) // 2
            elif other.y > points[max_y].y:
                # to the right and above
                if max_x > max_y:
                    pivot = (max_x - le + max_y) // 2
                else:
                    pivot = (max_x + max_y) // 2
            else:
                # straight to the right
                pivot = max_x
        else:
            if other.y < points[min_y].y:
                # straight below
                pivot = min_y
            elif other.y > points[max_y].y:
                # straight above
                pivot = max_y
            else:
                # Point may be within the polygon
                check = self._contains(other)
                if check > 0:
                    return -1
                    # Point inside polygon
                elif check == 0:
                    return 0
                    # Point lies on the edge
                else:
                    pivot = 0
                    # Point is near polygon, optimizing the pivot point
                    # selection becomes expensive
        dist = points[pivot].distance2(other)
        while True:
            cur_dist = points[pivot - 1].distance2(other)
            if cur_dist < dist:
                pivot -= 1
                dist = cur_dist
            else:
                break
        while True:
            if pivot == le - 1:
                pivot = pivot - le
            cur_dist = points[pivot + 1].distance2(other)
            if cur_dist < dist:
                pivot += 1
                dist = cur_dist
            else:
                break
        return min(dist, seg_distance(points[pivot], points[pivot - 1], other),
                   seg_distance(points[pivot], points[pivot + 1], other))
