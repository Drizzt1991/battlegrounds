import pyglet

from pyglet.gl import (
    GL_DEPTH_TEST,
    GL_MODELVIEW,
    GL_PROJECTION,
    glDisable,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glViewport,
)


class GameWindow(pyglet.window.Window):

    def __init__(self, world, *args, **kw):
        super().__init__(*args, **kw)
        self._world = world
        self.fps_display = pyglet.clock.ClockDisplay()
        pyglet.clock.schedule_interval(self._tick, 1 / 60)

    def _tick(self, dt):
        # Simulate movement
        self._world.tick(dt)

    def on_draw(self):
        self.clear()
        self.set_2d()
        self._world.draw()
        self.fps_display.draw()

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
