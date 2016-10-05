from abc import ABCMeta, abstractmethod, abstractproperty


class ABCWorld(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def tick(self, dt):
        raise NotImplementedError()


class ABCCollidable(object):
    __metaclass__ = ABCMeta

    # Collision geometry of the object
    shape = abstractproperty()


class ABCProp(object):
    """ Static objects in the world
    """
    __metaclass__ = ABCMeta

    # Static position of the object in the world
    position = abstractproperty()


class ABCActor(ABCCollidable):
    """ Actors are moving objects, like the player itself
    """

    position = abstractproperty()

    @abstractmethod
    def tick(self, dt):
        """ Simulate movement for this actor
        """
