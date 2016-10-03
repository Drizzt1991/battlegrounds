from abc import ABCMeta, abstractmethod
from engine.geometry import Circle


class ABCWorld(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def draw(self):
        raise NotImplementedError()

    @abstractmethod
    def tick(self, dt):
        raise NotImplementedError()


class ABCComponent(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def draw(self):
        raise NotImplementedError()

    @abstractmethod
    def tick(self, dt):
        raise NotImplementedError()


class CircleComponent(ABCComponent):

    def __init__(self, center, radius):
        self.shape = Circle()

    def draw(self):
        self._draw_shape()

    def tick(self, dt):
        pass


class Actor(ABCComponent):

    def tick(self, dt):
        pass


class World(ABCWorld):

    def __init__(self, world_map):
        self._components = []
        for component_conf in world_map['components']:
            self._components.append

    def draw(self):
        for component in self._components:
            component.draw()

    def tick(self):
        pass
