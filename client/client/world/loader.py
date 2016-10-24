import random
from engine.geometry import Circle, Vector, classify_polygon

from .props import SimpleProp


def shape_from_config(shape_conf):
    if shape_conf['type'] == "circle":
        x, y = shape_conf['center']
        return Circle(Vector(x, y), shape_conf['radius'])
    if shape_conf['type'] == "polygon":
        points = []
        for x, y in shape_conf['points']:
            points.append(Vector(x, y))
        return classify_polygon(points)
    else:
        raise ValueError(shape_conf['type'])


def load_props(world, world_map):
    props = []
    for prop_conf in world_map['props']:
        shape = shape_from_config(prop_conf['shape'])
        x, y = prop_conf['position']
        prop = SimpleProp(
            shape=shape, position=Vector(x, y))
        props.append(prop)

    for x in range(100000):
        x = random.randint(50, 10000)
        y = random.randint(50, 10000)
        c = Circle(Vector(0, 0), random.randint(2, 5))
        prop = SimpleProp(
            shape=c, position=Vector(x, y))
        props.append(prop)
    return props
