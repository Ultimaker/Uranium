class Event:
    MousePressEvent = 1
    MouseMoveEvent = 2
    MouseReleaseEvent = 3
    KeyPressEvent = 4
    KeyReleaseEvent = 5
    SceneChangeEvent = 6
    ToolActivateEvent = 7
    ToolDeactivateEvent = 8

    def __init__(self, type):
        super().__init__()
        self._type = type

    @property
    def type(self):
        return self._type

class MouseEvent(Event):
    LeftButton = "left"
    RightButton = "right"
    MiddleButton = "middle"

    def __init__(self, type, x = 0, y = 0, lastX = None, lastY = None, buttons = []):
        super().__init__(type)
        self._x = x
        self._y = y
        self._lastX = lastX
        self._lastY = lastY
        self._buttons = buttons

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def lastX(self):
        return self._lastX

    @property
    def lastY(self):
        return self._lastY

    @property
    def deltaX(self):
        if self._lastX != None:
            return self._x - self._lastX

        return 0

    @property
    def deltaY(self):
        if self._lastY != None:
            return self._y - self._lastY

        return 0

    @property
    def buttons(self):
        return self._buttons

class KeyEvent(Event):
    def __init__(self, type, key):
        super().__init__(type)
        self._key = key

    @property
    def key(self):
        return self._key

class SceneChangeEvent(Event):
    def __init__(self):
        super().__init__(self.SceneChangeEvent)

class ToolEvent(Event):
    def __init__(self, type):
        super().__init__(type)
