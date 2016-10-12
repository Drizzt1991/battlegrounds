import pyglet

from pyglet.gl import (
    GL_DEPTH_TEST,
    GL_MODELVIEW,
    GL_PROJECTION,
    glDisable,
    glEnable,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glViewport,
    gluPerspective,
    gluLookAt
)


class GameWindow(pyglet.window.Window):

    def __init__(self, world, scene, controller, camera, *args, **kw):
        super().__init__(*args, **kw)
        self._world = world
        self._scene = scene
        self._controller = controller
        self._camera = camera
        self.fps_display = pyglet.clock.ClockDisplay()
        pyglet.clock.schedule_interval(self._tick, 1 / 60)
        self.push_handlers(controller)

    def _tick(self, dt):
        # Simulate movement
        self._controller.tick(dt)
        self._world.tick(dt)

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

    def on_draw(self):
        self.clear()
        self.set_3d()
        self._scene.draw()
        self.set_2d()
        self.fps_display.draw()

    def on_resize(self, width, height):
        self.set_2d()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 20060.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Rotation is a unit vector on 2d ground plane, position in a 2d vector
        # of the position in the world.
        position, (ex, ey, ez) = self._camera.get_viewport()
        gluLookAt(
            ex, ey, ez, position.x, position.y, 5, 0, 0, 1)
