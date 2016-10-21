from abc import ABCMeta, abstractmethod


class BaseShape(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def bbox(self):
        """ Return an axis aligned bounding box for shape """
        raise NotImplementedError()

    @abstractmethod
    def contains(self, point):
        """ Containment test for point in shape. Returns True or False """
        raise NotImplementedError()

    @abstractmethod
    def distance(self, point):
        """ Distance from shape to point.
            Returns -1 if point is contained in object.
        """
        raise NotImplementedError()

    @abstractmethod
    def closest_point(self, point):
        """ Most likely to be similar to distance, but returns closest point
            on shape to point.
            Returns `point` itself if it's contained in shape.
        """
        raise NotImplementedError()

    @abstractmethod
    def intersects(self, shape):
        """ Check if 2 shapes intersect. Return None or manifold object.
            More info in `intersects.py`.
        """
        raise NotImplementedError()


class BaseIntersection(object):
    __metaclass__ = ABCMeta

    def __init__(self, shape, other):
        self.shape = shape
        self.other = other
