from .abc import ABCActor
from .constants import CHARACTER_RADIUS
from engine.geometry import Circle, Vector


class Actor(ABCActor):

    def __init__(self, world, position=Vector(0, 0)):
        self._world = world
        self._position = position

    @property
    def position(self):
        return self._position


class Character(Actor):

    shape = Circle(Vector(0, 0), CHARACTER_RADIUS)

    def tick(self, dt):
        self._position += Vector(10, 10) * dt
