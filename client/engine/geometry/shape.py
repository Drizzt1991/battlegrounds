from abc import ABCMeta, abstractmethod


class BaseShape(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def contains(self, vector):
        """ Containment test for point in shape """
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

    def __init__(self, shape1, shape2):
        self.shape1 = shape1
        self.shape2 = shape2
