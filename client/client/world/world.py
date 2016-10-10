from engine.geometry import Vector

from .abc import ABCWorld
from .actors import Character
from .loader import load_props


class World(ABCWorld):

    def __init__(self, world_map):
        self._props = load_props(self, world_map)
        self._actors = [
            Character(self, position=Vector(0, 0))]
        self._tick_period = 0.03125  # ~30 fps simulation
        self._timer = 0
        self._reminder = 0

    def tick(self, dt):
        period = self._tick_period
        dt = self._reminder + dt
        self._reminder = dt % period
        for _ in range(int(dt // period)):
            for actor in self._actors:
                actor.tick(period)
            self._timer += period

    @property
    def props(self):
        return self._props

    @property
    def actors(self):
        return self._actors

    @property
    def main_actor(self):
        return self._actors[0]
