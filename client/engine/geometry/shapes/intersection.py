""" All intersection functions
    Intersection is an operation, that allows to tell if 2 static shapes
    overlap and return the overlap manifold, that contains:
      * Points of contact
      * Penetration depth
      * Vector of resolution, or collision normal

    Example:

        a = AABB(Vector(0, 1), Vector(2, 3))
        b = AABB(Vector(0, 0), Vector(2, 2))
        manifold = intersect_aabb_aabb(a, b)
        assert manifold is not None

"""
from engine.geometry.vector import Vector

from .aabb import AABB
from .circle import Circle
from .polygon import Polygon, Triangle


class Manifold:

    def __init__(self, *, points=(), depth=0, normal=Vector(1, 0)):
        points = points
        depth = depth
        normal = normal


def intersect_aabb_aabb(a: AABB, b: AABB) -> Manifold:
    if b.min.x > a.max.x or b.min.y > a.max.y:
        return None
    if b.max.x < a.min.x or b.max.y < a.min.y:
        return None
    return Manifold()


def intersect_aabb_circle(aabb: AABB, circle: Circle) -> Manifold:
    if (aabb.distance2(circle.center) - circle.radius**2 > 0):
        return None
    return Manifold()


def intersect_aabb_triangle(aabb: AABB, triangle: Triangle) -> Manifold:
    """ Will use the Separating Axes Test for this. The axes can be one of:
        * 2 normals for aabb edges
        * 3 normals for triangle edges
    """
    a, b, c = triangle._a, triangle._b, triangle._c
    aabb_min, aabb_max = aabb._min, aabb._max
    # Test X axis separation
    t_min = min(a.x, b.x, c.x)
    t_max = max(a.x, b.x, c.x)
    if t_max < aabb_min.x or t_min > aabb_max.y:
        return None
    # Test Y axis separation
    t_min = min(a.y, b.y, c.y)
    t_max = max(a.y, b.y, c.y)
    if t_max < aabb_min.y or t_min > aabb_max.y:
        return None

    # Next test 3 triangle normals
    aabb_a, aabb_b = Vector(aabb_min.x, aabb_max.y), \
        Vector(aabb_max.x, aabb_min.y)
    points = [aabb_min, aabb_a, aabb_max, aabb_b]
    # Test AB's normal
    ab_normal = (b - a).rotate_deg(90)
    proj = [ab_normal.dot(p) for p in points]
    if max(proj) < ab_normal.dot(a):
        return None
    # C will always be positive, as triangle is ordered clockwise
    if min(proj) > ab_normal.dot(c):
        return None

    # Test BC's normal
    bc_normal = (c - b).rotate_deg(90)
    proj = [bc_normal.dot(p) for p in points]
    if max(proj) < bc_normal.dot(b):
        return None
    if min(proj) > bc_normal.dot(a):
        return None

    # Test CA's normal
    ca_normal = (a - c).rotate_deg(90)
    proj = [ca_normal.dot(p) for p in points]
    if max(proj) < ca_normal.dot(c):
        return None
    if min(proj) > ca_normal.dot(b):
        return None

    return Manifold()


def intersect_aabb_polygon(aabb: AABB, polygon: Polygon) -> Manifold:
    raise NotImplementedError()


def intersect_circle_circle(a: Circle, b: Circle) -> Manifold:
    d2 = a._c.distance2(b._c)
    r2 = (a._r + b._r) ** 2
    if d2 > r2:
        return None
    return Manifold()


def intersect_circle_triangle(circle: Circle, triangle: Triangle) -> Manifold:
    closest = triangle._closest_point(circle.center)
    if ((closest.distance2(circle.center) - circle.radius ** 2) > 0):
        return None
    return Manifold()


def intersect_circle_polygon(circle: Circle, polygon: Polygon) -> Manifold:
    d = polygon.distance(circle.center)
    if (d - circle.radius > 0):
        return None
    return Manifold()


def intersect_triangle_triangle(a: Triangle, b: Triangle) -> Manifold:
    raise NotImplementedError()


def intersect_triangle_polygon(triangle: Triangle, polygon: Polygon) \
        -> Manifold:
    raise NotImplementedError()


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


def intersect_polygon_polygon(a: Polygon, b: Polygon) -> Manifold:
    # Check our polygon normal's
    points = a.points
    prev_point = points[-1]
    for point in points:
        normal = (point - prev_point).rotate_deg(90)
        if not _sat_test(a, b, normal):
            return None
        prev_point = point

    # Check other polygon's normals
    points = b.points
    prev_point = points[-1]
    for point in points:
        normal = (point - prev_point).rotate_deg(90)
        if not _sat_test(a, b, normal):
            return None
        prev_point = point

    return Manifold()
