from .abc import ABCProp


class SimpleProp(ABCProp):

    def __init__(self, shape, position):
        self._shape = shape
        self._position = position

    @property
    def shape(self):
        return self._shape

    @property
    def position(self):
        return self._position
