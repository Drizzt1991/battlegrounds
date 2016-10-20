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
    def get_height(self):
        """ Returns tree height. Useful for debugging issues
        """
        raise NotImplementedError()

    @abstractmethod
    def add(self, object):
        """ Add object to broad phase queries. object.shape should be
            object's shape.
            Returns: node_id of the created node
        """
        raise NotImplementedError()

    @abstractmethod
    def remove(self, node_id):
        """ Remove previously added object. If node_id not present
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
