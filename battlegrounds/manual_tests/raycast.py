import argparse

from engine.geometry import AABB, Circle, Polygon, Triangle, Vector
from engine.geometry.line import Segment

from engine._testutil import debug_draw


def get_parser():
    parser = argparse.ArgumentParser(
        description='Raycast test')
    parser.add_argument(
        '--shape', help='One of: cirlce, polygon, triangle',
        default="polygon")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    points = [[0, 5], [-1, 4], [-2, 1], [-2, 0], [-1, -3], [0, -5]]
    poly = Polygon([Vector(*p) for p in points]).translate(Vector(0.5, 0))
    shapes = {
        "cirlce": Circle(Vector(0, 0), radius=2),
        "polygon": poly,
        "triangle": Triangle([Vector(-2, 2), Vector(0, -2), Vector(4, 4)]),
        "aabb": AABB(Vector(-3.5, -2.5), Vector(1, 4))
    }
    shape = shapes[args.shape]
    segments = []
    for angle in range(360, step=1):
        d = Vector.polar_deg(angle)
        p = d * -10
        t = shape.raycast(p, d)
        p2 = p + d * t
        segments.append(Segment(p, p2))

    debug_draw(shape, *segments)


if __name__ == "__main__":
    main()
