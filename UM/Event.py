# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

##  \file Event.py
#   Contains the Event class and important subclasses used throughout UM.


##  Base event class.
#   Defines the most basic interface for events and several constants to identify event types.
class Event:
    MousePressEvent = 1
    MouseMoveEvent = 2
    MouseReleaseEvent = 3
    KeyPressEvent = 4
    KeyReleaseEvent = 5
    SceneChangeEvent = 6
    ToolActivateEvent = 7
    ToolDeactivateEvent = 8
    MouseWheelEvent = 9
    CallFunctionEvent = 10
    ViewActivateEvent = 11
    ViewDeactivateEvent = 12

    def __init__(self, event_type):
        super().__init__()
        self._type = event_type

    ##  The type of event.
    @property
    def type(self):
        return self._type


##  Mouse Event class.
#   This class represents a mouse event. It has properties corresponding to important mouse
#   event properties and constants for mouse buttons.
class MouseEvent(Event):
    ## Left mouse button.
    LeftButton = "left"
    RightButton = "right"
    MiddleButton = "middle"

    ##  Initialize.
    #   \param type The type of event. \sa Event
    #   \param x The X coordinate of the event.
    #   \param y The Y coordinate of the event.
    #   \param last_x The X coordinate of the previous mouse event. Can be None. It is used to calculate deltaX.
    #   \param last_y The Y coordinate of the previous mouse event. Cam be None. It is used to calculate deltaY.
    #   \param buttons The buttons that are associated with this event.
    def __init__(self, event_type, x = 0, y = 0, last_x = None, last_y = None, buttons = None): #pylint: disable=bad-whitespace
        super().__init__(event_type)
        self._x = x
        self._y = y
        self._last_x = last_x
        self._last_y = last_y
        self._buttons = []
        if buttons:
            self._buttons = buttons

    ##  The X coordinate of the event.
    @property
    def x(self):
        return self._x

    ##  The Y coordinate of the event.
    @property
    def y(self):
        return self._y

    ##  The X coordinate of the previous event.
    @property
    def lastX(self):
        return self._last_x

    ##  The Y coordinate of the previous event.
    @property
    def lastY(self):
        return self._last_y

    ##  The change in X position between this event and the previous event.
    @property
    def deltaX(self):
        if self._last_x != None:
            return self._x - self._last_x

        return 0

    ##  The change in Y position between this event and the previous event.
    @property
    def deltaY(self):
        if self._last_y != None:
            return self._y - self._last_y

        return 0

    ##  The list of buttons associated with this event.
    @property
    def buttons(self):
        return self._buttons


class WheelEvent(Event):
    def __init__(self, horizontal, vertical):
        super().__init__(Event.MouseWheelEvent)
        self._horizontal = horizontal
        self._vertical = vertical

    @property
    def horizontal(self):
        return self._horizontal

    @property
    def vertical(self):
        return self._vertical


##  Key Event class.
class KeyEvent(Event):
    ShiftKey = 1
    ControlKey = 2
    AltKey = 3
    MetaKey = 4
    SpaceKey = 5
    EnterKey = 6
    UpKey = 7
    DownKey = 8
    LeftKey = 9
    RightKey = 10
    EscapeKey = 11
    MinusKey = 12
    UnderscoreKey = 13
    PlusKey = 14
    EqualKey = 15

    def __init__(self, event_type, key):
        super().__init__(event_type)
        self._key = key

    @property
    def key(self):
        return self._key


##  Tool related event class.
class ToolEvent(Event):
    pass

##  Event used to call a function.
class CallFunctionEvent(Event):
    def __init__(self, function, args, kwargs):
        super().__init__(Event.CallFunctionEvent)
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def call(self):
        self._function(*self._args, **self._kwargs)


##  View related event class.
class ViewEvent(Event):
    pass
