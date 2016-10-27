import math

from engine.utils import lazy_property

from .aabb import AABB
from .circle import Circle
from .shape import BaseIntersection, BaseShape
from ..utils import orient, seg_closest, seg_distance
from ..vector import Vector


def _check_convex(points):
    prev_edge = [points[-2], points[-1]]
    for point in points:
        o = orient(prev_edge[0], prev_edge[1], point)
        if o < 0:
            return False
        elif o == 0:
            raise ValueError("3 Points on single line {}".format(
                (prev_edge[0], prev_edge[1], point)))
        prev_edge.pop(0)
        prev_edge.append(point)
    return True


def classify_polygon(points):
    """ Factory for polygons, will analyze points and return an instance of
        this polygon
    """
    if len(points) == 3:
        if orient(*points) < 0:
            points.reverse()
        return Triangle(points)
    if len(points) == 4:
        # TEST AABB
        a, b, c, d = sorted(points, key=lambda k: (k.x, k.y))
        if a.x == b.x and c.x == d.x and a.y == c.y and b.y == d.y:
            # Check for ribbon case
            if (points.index(a) - points.index(d)) % 2 == 0:
                return AABB(a, d)
    if not _check_convex(points):
        # Try to reverse points, in case of clockwise input
        points.reverse()
        if not _check_convex(points):
            raise NotImplementedError("Concave polygons not supported")
    return Polygon(points)


def _raycast(point, direction, vertices, normals):
    """
        "Real Time Collision Detection" does have this algorithm descibed in
    `Intersecting Ray or Segment Against Convex Polyhedron`
    While the algorithm is for 3D, it's easy to understand 2D concept
        The idea is to find all intersections between ray and edges of the
    polygon, but check if the ray hits it `behind` or `upfront`, forming the
    `entering` and `exiting` points. If those 2 point sets, projected onto the
    ray do not intersect, we have a ray hit, and our hit distance is the
    maximum of `entering` points. We could also get the exiting point by this
    algorithm for free, as it's the minimum of `exiting` point set.

    """
    t_min, t_max = 0.0, float('inf')
    tagged_normal = None
    for normal, vertex in zip(normals, vertices):
        # Distance from vertex to point projected onto normal, with INVERTED
        # sign
        numerator = normal.dot(vertex - point)  # numerator
        # direction's projection onto this edge normal
        denominator = normal.dot(direction)

        if denominator == 0.0:
            if numerator < 0.0:
                # Ray is parallel to edge and is outside of polygon's
                # halfplane
                return None
        else:
            t = numerator / denominator
            if denominator < 0.0 and t > t_min:
                # The segment enters this half-space.
                t_min = t
                tagged_normal = normal
            elif denominator > 0.0 and t < t_max:
                # The segment exits this half-space.
                t_max = t

        if t_max < t_min:
            return None

    if tagged_normal is not None:
        return t_min

    return None


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
    """ Same as polygon we assume points are counter-clockwise """

    def __init__(self, points):
        assert len(points) == 3
        assert orient(*points) > 0
        self._a, self._b, self._c = points

    def __eq__(self, other):
        if isinstance(other, Triangle):
            return self._a == other._a and self._b == other._b and \
                self._c == other._c
        return False

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

    @lazy_property
    def normals(self):
        points = (self._a, self._b, self._c)
        normals = []
        prev_point = points[-1]
        for point in points:
            normal = (point - prev_point).rotate_deg(-90)
            normals.append(normal)
            prev_point = point
        return normals

    def contains(self, other):
        assert isinstance(other, Vector)
        a, b, c = self._a, self._b, self._c
        if orient(a, b, other) < 0:
            return False
        if orient(b, c, other) < 0:
            return False
        if orient(c, a, other) < 0:
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

    closest_point = _closest_point

    def distance(self, other):
        assert isinstance(other, Vector)
        x = self._closest_point(other)
        if other is x:
            return -1
        return x.distance(other)

    def intersects(self, other):
        if isinstance(other, Circle):
            return intersect_circle_triangle(other, self)
        if isinstance(other, Polygon):
            return intersect_triangle_polygon(self, other)
        elif isinstance(other, Triangle):
            return intersect_triangle_triangle(self, other)
        elif isinstance(other, AABB):
            return intersect_aabb_triangle(other, self)
        raise ValueError(other)

    def raycast(self, point, direction):
        vertices = self.points
        normals = self.normals
        return _raycast(point, direction, vertices, normals)


class PolygonIntersection(BaseIntersection):
    pass


class Polygon(BaseShape):
    """ We assume that the polygon is convex and ordered counter-clockwise """

    def __init__(self, points):
        assert orient(*points[:3]) > 0
        self._points = tuple(points)

    def __eq__(self, other):
        if isinstance(other, Polygon):
            return self._points == other._points
        return False

    def __hash__(self):
        return hash((self.__class__, self._points))

    def __repr__(self):
        return "Polygon({})".format(list(self.points))

    def bbox(self):
        p = self._points
        min_x, min_y, max_x, max_y = self._min_max
        return AABB(
            Vector(p[min_x].x, p[min_y].y), Vector(p[max_x].x, p[max_y].y))

    @lazy_property
    def center(self):
        """ Center of a tight AABB around this polygon
        """
        return self.bbox().center

    @lazy_property
    def _min_max(self):
        """ 4 indices, of min_x, min_y, max_x, max_y points. They can be equal
        """
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
        return min_x, min_y, max_x, max_y

    @property
    def points(self):
        return self._points

    @lazy_property
    def normals(self):
        points = self._points
        normals = []
        prev_point = points[-1]
        for point in points:
            normal = (point - prev_point).rotate_deg(-90)
            normals.append(normal)
            prev_point = point
        return normals

    def _contains(self, other):
        """ Subroutine for containment checks. Returns:
            * -1 if point outside of polygon
            * 0 if point inside, but not on border
            * 1 of points of the edge, that contain t
        """
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
        if isinstance(other, Polygon):
            return intersect_polygon_polygon(self, other)
        elif isinstance(other, Triangle):
            return intersect_triangle_polygon(other, self)
        elif isinstance(other, Circle):
            return intersect_circle_polygon(other, self)
        elif isinstance(other, AABB):
            return intersect_aabb_polygon(other, self)
        raise ValueError(other)

    def _closest_point(self, other):
        # import pdb
        # pdb.set_trace()
        points = self._points
        le = len(points)
        # Choose pivot by bounding AABB sections first
        pivot = self._choose_pivot(other)
        # If None - point is inside of bounding AABB, so we need to check for
        # containment in polygon
        if pivot is None:
            # Point may be within the polygon
            check = self._contains(other)
            if check > 0:
                # Point lies on polygon
                return other, -1
            elif check == 0:
                # Point lies on border
                return other, 0
            # No way to optimize
            pivot = 0

        # Decide on climbing direction and find edge facing the point
        p1 = points[(pivot + 1) % le]
        up_face = orient(points[pivot], p1, other)
        down_face = orient(points[pivot - 1], points[pivot], other)
        dist = None

        if up_face > 0 and down_face > 0:
            # We have not idea what direction is best, as it on other side of
            # polygon. Just go down, and we can skip 1st point already
            pivot = pivot - 1
            direction = -1
            # Iterate until edge is facing the point, we will climb from there
            while True:
                p = (pivot - 1) % le
                o = orient(points[p], points[pivot], other)
                pivot = p
                if o < 0:
                    break
        elif up_face < 0:
            if down_face > 0:
                # We will go up if down edge is not facing the point
                direction = 1
            else:
                dist = points[pivot].distance2(other)
                up_dist = p1.distance2(other)
                # We will go up if distance is lower (extremum is that way)
                if up_dist < dist:
                    pivot = (pivot + 1) % le
                    dist = up_dist
                    direction = 1
                else:
                    direction = -1
        else:
            direction = -1

        if dist is None:
            dist = points[pivot].distance2(other)

        # Climb the hill in direction
        while True:
            p = (pivot + direction) % le
            if orient(points[pivot], points[p], other) > 0:
                # We passed last point facing our direction. Pivot is the
                # extremum
                break
            cur_dist = points[p].distance2(other)
            if cur_dist < dist:
                pivot = p
                dist = cur_dist
            else:
                break

        p0 = points[pivot]
        p1 = seg_closest(p0, points[pivot - 1], other)
        p2 = seg_closest(p0, points[(pivot + 1) % le], other)
        p1_dist = p1.distance2(other)
        p2_dist = p2.distance2(other)
        if dist < p1_dist and dist < p2_dist:
            return p0, math.sqrt(dist)
        elif p1_dist < p2_dist:
            return p1, math.sqrt(p1_dist)
        else:
            return p2, math.sqrt(p2_dist)

    def closest_point(self, other):
        assert isinstance(other, Vector)
        point, dist = self._closest_point(other)
        return point

    def distance(self, other):
        assert isinstance(other, Vector)
        point, dist = self._closest_point(other)
        return dist

    def _choose_pivot(self, other):
        """ Fast function to choose some point to start the climbing algorithm
        in distance and closest point routines
        """
        points = self._points
        le = len(points)
        min_x, min_y, max_x, max_y = self._min_max
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
                # Point is near polygon, optimizing the pivot point
                # selection becomes expensive
                return None
        return pivot

    def raycast(self, point, direction):
        vertices = self.points
        normals = self.normals
        return _raycast(point, direction, vertices, normals)

    def translate(self, dv):
        return Polygon([p + dv for p in self.points])


from .intersection import (  # noqa
    intersect_triangle_triangle,
    intersect_circle_triangle,
    intersect_aabb_triangle,
    intersect_triangle_polygon,
    intersect_polygon_polygon,
    intersect_circle_polygon,
    intersect_aabb_polygon
)
