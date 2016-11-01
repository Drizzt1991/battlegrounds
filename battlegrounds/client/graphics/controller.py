from collections import defaultdict

from pyglet.window import key, mouse


class InputController(object):
    """ Listens to key events, translates them into game operations like pawn
        movement and so on.
    """

    MOUSE_SENSITIVITY = 0.35  # radians per mouse pixel

    def __init__(self, camera, actor):
        self._camera = camera
        self._actor = actor
        self._actions = defaultdict(set)

        self.key_bindings = {
            "up": (key.UP, key.W),
            "down": (key.DOWN, key.S),
            "rotate_right": (key.D, ),
            "rotate_left": (key.A, ),
            "strafe_right": (key.RIGHT, ),
            "strafe_left": (key.LEFT, ),

        }
        self._reverse_bindings = {}
        for action, keys in self.key_bindings.items():
            for k in keys:
                self._reverse_bindings[k] = action
        self._lock_camera = False
        # Apply the mouse drag on tick, so we don't have lags in camera
        # movement
        self._pending_mouse_drag = 0

    def on_key_press(self, symbol, modifiers):
        action = self._reverse_bindings.get(symbol)
        if action:
            self._actions[action].add(symbol)

    def on_key_release(self, symbol, modifiers):
        action = self._reverse_bindings.get(symbol)
        if action:
            self._actions[action].discard(symbol)

    def tick(self, dt):
        # Apply camera rotation
        if self._pending_mouse_drag:
            rot = self._camera.rotation.rotate_deg(
                self.MOUSE_SENSITIVITY * self._pending_mouse_drag)
            self._camera.rotation = rot
            self._pending_mouse_drag = 0

        # Process forward/backword movement
        both_mouse = self._actions['mouse_right'] and \
            self._actions['mouse_left']
        if self._actions['up']:
            self._actor.movement.movement = 1
        elif self._actions['down']:
            if not both_mouse:
                self._actor.movement.movement = -1
            else:
                # We have a conflict here, and somehow stopping seems more
                # reasonable
                self._actor.movement.movement = 0
        elif both_mouse:
            self._actor.movement.movement = 1
        else:
            self._actor.movement.movement = 0

        # Process rotation.
        if self._actions['rotate_right'] and not self._actions['rotate_left']:
            rotation = -1
        elif self._actions['rotate_left'] and not \
                self._actions['rotate_right']:
            rotation = 1
        else:
            rotation = 0
        # Note, that if we are locked to camera we can't actually rotate,
        # rather we will just perform strafe
        if not self._actions['mouse_right']:
            self._actor.movement.rotation = rotation
        else:
            self._actor.movement.rotation = 0
            self._actor.movement.strafe = rotation

        # Process strafe
        if self._actions['strafe_right'] and not self._actions['strafe_left']:
            self._actor.movement.strafe = -1
        elif self._actions['strafe_left'] and not \
                self._actions['strafe_right']:
            self._actor.movement.strafe = 1
        elif not self._actions['mouse_right']:
            self._actor.movement.strafe = 0

        # If right mouse button is pressed we lock movement of character to
        # camera direction
        some_movement = self._actor.movement.movement or \
            self._actor.movement.strafe
        if self._actions['mouse_right'] and some_movement:
            self._actor.movement.forward = self._camera.rotation

        # If we released mouse buttons
        if self._lock_camera and some_movement:
            # We will pick up camera last viewport and lock from there
            self._actor.movement.forward = self._camera.rotation
            self._camera.rotation = None
            self._lock_camera = False
        elif self._lock_camera and self._actor.movement.rotation:
            # If we rotate after releasing mouse buttons we will lock on last
            # player position instead
            self._camera.rotation = None
            self._lock_camera = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button & mouse.RIGHT:
            self._actions['mouse_right'] = True
        if button & mouse.LEFT:
            self._actions['mouse_left'] = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button & mouse.RIGHT:
            self._actions['mouse_right'] = False
            # Left mouse button was pressed last, lock camera to character
            if not self._actions['mouse_left']:
                self._lock_camera = True
        if button & mouse.LEFT:
            self._actions['mouse_left'] = False
            # Left mouse button was pressed last, set free camera
            if not self._actions['mouse_right']:
                self._camera.rotation = self._camera.rotation

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT or buttons & mouse.RIGHT:
            self._pending_mouse_drag += dx

    # def on_mouse_motion(x, y, dx, dy):
    #     pass

    # def on_mouse_scroll(x, y, scroll_x, scroll_y):
    #     pass

    # def on_mouse_enter(x, y):
    #     pass

    # def on_mouse_leave(x, y):
    #     pass
