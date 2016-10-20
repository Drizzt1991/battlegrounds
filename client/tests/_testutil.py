import math
import sys
import unittest

from engine.geometry.shapes.shape import BaseShape

# We just don't want to import pyglet if it's not needed. It will do dumb stuff
# on import.
_Drawer = None


def create_drawer():
    global _Drawer
    if _Drawer is not None:
        return _Drawer()

    from pyglet import gl
    import pyglet

    def draw_circle(x, y, radius, iterations=None):
        """ Draw circle in OpenGL context
        """
        if iterations is None:
            iterations = int(2 * radius * math.pi)
        s = math.sin(2 * math.pi / iterations)
        c = math.cos(2 * math.pi / iterations)

        dx, dy = radius, 0

        points = [x, y]
        for i in range(iterations + 1):
            points.extend((x + dx, y + dy))
            dx, dy = (dx * c - dy * s), (dy * c + dx * s)

        bg = gl.GL_TRIANGLE_FAN, ('v2f', tuple(points))
        fg = gl.GL_LINE_LOOP, ('v2f', tuple(points[2:]))
        return bg, fg

    class Drawer(object):

        def draw(self, shapes):
            background = []
            foreground = []
            for shape in shapes:
                if isinstance(shape, BaseShape):
                    bg, fg = self.draw_shape(shape)
                    foreground.append(fg)
                    background.append(bg)
                elif hasattr(shape, "_root"):
                    bg, fg = self.draw_dynamicaabb(shape)
                    foreground.extend(fg)
                    background.extend(bg)

            gl.glColor3f(0.0, 0.7, 0.7)
            for draw_type, draw_points in background:
                pyglet.graphics.draw(
                    len(draw_points[1]) // 2, draw_type, draw_points)
            gl.glColor3f(0.8, 0.8, 0.8)
            for draw_type, draw_points in foreground:
                pyglet.graphics.draw(
                    len(draw_points[1]) // 2, draw_type, draw_points)

        def draw_shape(self, shape):
            draw_func = "draw_shape_" + shape.__class__.__name__.lower()
            draw_func = getattr(self, draw_func)
            return draw_func(shape)

        def draw_shape_circle(self, circle):
            center = circle.center
            # We have no need for unit perfect circle, as we will still have a
            # projection in the game.
            return draw_circle(center.x, center.y, circle.radius, 32)

        def draw_shape_aabb(self, aabb):
            x_min, y_min, x_max, y_max = \
                aabb.min.x, aabb.min.y, aabb.max.x, aabb.max.y
            bg = (
                gl.GL_TRIANGLE_FAN,
                ('v2f', (x_min, y_min, x_min, y_max,
                         x_max, y_max, x_max, y_min)))
            fg = (
                gl.GL_LINE_LOOP,
                ('v2f', (x_min, y_min, x_min, y_max,
                         x_max, y_max, x_max, y_min)))
            return bg, fg

        def draw_shape_triangle(self, triangle):
            points = []
            for point in triangle.points:
                points.extend((point.x, point.y))
            bg = (
                gl.GL_TRIANGLES,
                ('v2f', tuple(points))
            )
            fg = (
                gl.GL_LINE_LOOP,
                ('v2f', tuple(points))
            )
            return bg, fg

        def draw_shape_polygon(self, polygon):
            points = polygon.points
            p = []
            for point in points:
                p.extend((point.x, point.y))
            bg = (
                gl.GL_TRIANGLE_FAN,
                ('v2f', p)
            )
            fg = (
                gl.GL_LINE_LOOP,
                ('v2f', p)
            )
            return bg, fg

        def draw_dynamicaabb(self, dynamic_aabb):
            nodes = [dynamic_aabb._root]
            foreground, background = [], []
            while nodes:
                siblings = []
                for node in nodes:
                    bg, fg = self.draw_shape_aabb(node.aabb)
                    foreground.append(fg)
                    if node.leaf:
                        bg, fg = self.draw_shape(node.obj.shape)
                        foreground.append(fg)
                        background.append(bg)
                    else:
                        siblings.append(node.left)
                        siblings.append(node.right)
                nodes = siblings
            return background, foreground

        def draw_scale(self):
            gl.glColor3f(0.5, 0.5, 0.5)
            # axises
            pyglet.graphics.draw(
                4, gl.GL_LINES,
                ("v2f", (0, -100, 0, 100, -100, 0, 100, 0)),
            )
            lines = []
            line_width = 0.1
            for i in range(-20, 20):
                lines.extend((-line_width, i, line_width, i))
                lines.extend((i, -line_width, i, line_width))
            pyglet.graphics.draw(
                len(lines) // 2, gl.GL_LINES,
                ("v2f", lines),
            )

    _Drawer = Drawer
    return _Drawer()


def debug_draw(*p, width=20):
    import pyglet

    if not p:
        p = []
        l = sys._getframe(1).f_locals
        for x in l.values():
            if isinstance(x, BaseShape):
                p.append(x)

    w = pyglet.window.Window()
    drawer = create_drawer()

    data = {
        "scale": 1.0,
        "dx": 0.0,
        "dy": 0.0
    }

    @w.event
    def on_draw():
        w.clear()
        w_width, w_height = w.get_size()
        height = (width / w_width) * w_height
        pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)
        pyglet.gl.glViewport(0, 0, w_width, w_height)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, width, 0, height, -1, 1)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()
        dx = (data['dx'] / w_width) * width
        dy = (data['dy'] / w_width) * width
        pyglet.gl.glTranslatef(width // 2 + dx, height // 2 + dy, 0)
        pyglet.gl.glScalef(data['scale'], data['scale'], 0)
        drawer.draw(p)
        drawer.draw_scale()

    @w.event
    def on_text(text):
        if text == "+":
            data["scale"] *= 1.5
        if text == "-":
            data["scale"] /= 1.5

    @w.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        data['dx'] += dx
        data['dy'] += dy

    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        pass


class ShapeTestCase(unittest.TestCase):

    debug_draw = debug_draw
