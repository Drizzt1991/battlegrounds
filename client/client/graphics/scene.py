from .utils import draw_circle


class Scene(object):

    def __init__(self, world):
        self._world = world

    def draw(self):
        for prop in self._world.props:
            self.draw_shape(prop.shape, prop.position)
        for actor in self._world.actors:
            self.draw_shape(actor.shape, actor.position)

    def draw_shape(self, shape, position):
        draw_func = "draw_shape_" + shape.__class__.__name__.lower()
        draw_func = getattr(self, draw_func)
        draw_func(shape, position)

    def draw_shape_circle(self, circle, position):
        center = position + circle.center
        draw_circle(center.x, center.y, circle.radius)
