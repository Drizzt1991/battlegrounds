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

    def __init__(self, world, scene, *args, **kw):
        super().__init__(*args, **kw)
        self._world = world
        self._scene = scene
        self.fps_display = pyglet.clock.ClockDisplay()
        pyglet.clock.schedule_interval(self._tick, 1 / 60)

    def _tick(self, dt):
        # Simulate movement
        self._world.tick(dt)

    def on_draw(self):
        self.clear()
        self._scene.draw()
        self.fps_display.draw()

    def on_resize(self, width, height):
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
