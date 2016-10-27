

class Ray:

    def __init__(self, origin, direction):
        self._origin = origin
        self._direction = direction

    @property
    def origin(self):
        return self._origin

    @property
    def direction(self):
        return self._direction


class Segment(Ray):

    def __init__(self, p1, p2):
        self._origin = p1
        self._pivot = p2
        self._direction = (p2 - p1).unit()
        self._distance = (p2 - p1).length()

    @property
    def pivot(self):
        return self._pivot

    @property
    def distance(self):
        return self._distance
