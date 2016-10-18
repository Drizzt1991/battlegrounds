from abc import ABCMeta, abstractmethod


class ABCBroadPhase(object):
    __metaclass__ = ABCMeta

    '''
    - addition
    - removal
    - pair management    ???
    - volume queries
    - movement           ???
    - ray casts
    '''

    @abstractmethod
    def add(self, object):
        """ Add object to broad phase queries. object.shape should be
            object's shape.
        """
        raise NotImplementedError()

    @abstractmethod
    def remove(self, object):
        """ Remove previously added object. If object is not added
            raises KeyError()
        """
        raise NotImplementedError()

    @abstractmethod
    def query_shape(self, shape):
        """ Return objects, that intersect this shape.
        """
        raise NotImplementedError()

    @abstractmethod
    def raycast(self, point, direction):
        """ Return an object, that was first hit by this ray """
        raise NotImplementedError()

    @abstractmethod
    def query_point(self, point):
        """ Return objects, that contain this point
        """
        raise NotImplementedError()

    @abstractmethod
    def closest(self, point):
        """ Return an iterator of objects closest to this point
        """
        raise NotImplementedError()
