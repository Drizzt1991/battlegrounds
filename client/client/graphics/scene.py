from pyglet.gl import (
    glPushMatrix, glPopMatrix, glTranslatef, gluNewQuadric, gluSphere,
    GL_LINES, GL_LINE_LOOP
)
from pyglet.graphics import draw

ROTATOR_LENGTH = 20


class Scene(object):

    def __init__(self, world):
        self._world = world

    def draw(self):
        for prop in self._world.props:
            self.draw_shape(prop.shape, prop.position)
        for actor in self._world.actors:
            self.draw_shape(actor.shape, actor.position)
            self.draw_rotator(actor.movement.forward, actor.position)

    def draw_shape(self, shape, position):
        draw_func = "draw_shape_" + shape.__class__.__name__.lower()
        draw_func = getattr(self, draw_func)
        draw_func(shape, position)

    def draw_shape_circle(self, circle, position):
        glPushMatrix()
        center = position + circle.center
        # We have no need for unit perfect circle, as we will still have a
        # projection in the game.
        # draw_circle(center.x, center.y, circle.radius, iterations=32)
        glTranslatef(center.x, center.y, 0)
        sphere = gluNewQuadric()
        gluSphere(sphere, circle.radius, 32, 5)
        glPopMatrix()

    def draw_shape_aabb(self, aabb, position):
        glPushMatrix()
        glTranslatef(position.x, position.y, 0)
        x_min, y_min, x_max, y_max = \
            aabb.min.x, aabb.min.y, aabb.max.x, aabb.max.y
        draw(
            4, GL_LINE_LOOP,
            ('v2f', (x_min, y_min, x_min, y_max, x_max, y_max, x_max, y_min))
        )
        glPopMatrix()

    def draw_shape_triangle(self, triangle, position):
        glPushMatrix()
        glTranslatef(position.x, position.y, 0)
        points = []
        for point in triangle.points:
            points.extend((point.x, point.y))
        draw(
            3, GL_LINE_LOOP,
            ('v2f', points)
        )
        glPopMatrix()

    def draw_rotator(self, rotation, position):
        end = position + rotation * ROTATOR_LENGTH
        draw(
            2, GL_LINES,
            ('v2f', (position.x, position.y, end.x, end.y))
        )
