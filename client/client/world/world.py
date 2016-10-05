from engine.geometry import Vector

from .abc import ABCWorld
from .actors import Character
from .loader import load_props


class World(ABCWorld):

    def __init__(self, world_map):
        self._props = load_props(self, world_map)
        self._actors = [
            Character(self, position=Vector(0, 0))]

    def tick(self, dt):
        for actor in self._actors:
            actor.tick(dt)

    @property
    def props(self):
        return self._props

    @property
    def actors(self):
        return self._actors
