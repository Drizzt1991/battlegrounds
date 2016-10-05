from engine.geometry import Circle, Vector

from .props import SimpleProp


def shape_from_config(shape_conf):
    if shape_conf['type'] == "circle":
        x, y = shape_conf['center']
        return Circle(Vector(x, y), shape_conf['radius'])
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
    return props