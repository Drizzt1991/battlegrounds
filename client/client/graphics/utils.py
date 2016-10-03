import math

from pyglet.gl import (
    GL_TRIANGLE_FAN,
    glBegin,
    glEnd,
    glVertex2f
)


def draw_circle(x, y, radius):
    """ Draw circle in OpenGL context
    """
    iterations = int(2 * radius * math.pi)
    s = math.sin(2 * math.pi / iterations)
    c = math.cos(2 * math.pi / iterations)

    dx, dy = radius, 0

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(iterations + 1):
        glVertex2f(x + dx, y + dy)
        dx, dy = (dx * c - dy * s), (dy * c + dx * s)
    glEnd()
