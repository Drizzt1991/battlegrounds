from abc import ABCMeta, abstractmethod


class BaseShape(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def contains(self, vector):
        """ Containment test for point in shape. Returns True or False """
        raise NotImplementedError()

    @abstractmethod
    def distance(self, vector):
        """ Distance from shape to point.
            Returns -1 if point is contained in object.
        """
        raise NotImplementedError()

    @abstractmethod
    def intersects(self, shape):
        """ Check if 2 shapes intersect. Return None or intersection object """
        raise NotImplementedError()


class BaseIntersection(object):
    __metaclass__ = ABCMeta

    def __init__(self, shape, other):
        self.shape = shape
        self.other = other
