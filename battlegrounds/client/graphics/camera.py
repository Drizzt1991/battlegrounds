
class Camera(object):

    HIGHT = 100

    def __init__(self, actor):
        self._actor = actor
        self._rotation = None  # If None - will lock on actor

    @property
    def rotation(self):
        if self._rotation is None:
            return self._actor.movement.forward
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value

    def get_viewport(self):
        position = self._actor.position
        rotation = self.rotation
        # Calculate eye position
        eye_position = position - rotation * self.HIGHT * 0.3
        return position, (eye_position.x, eye_position.y, self.HIGHT)
