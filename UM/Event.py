# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

##  \file Event.py
#   Contains the Event class and important subclasses used throughout UM.


##  Base event class.
#   Defines the most basic interface for events and several constants to identify event types.
from typing import List, Any, Callable


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

    def __init__(self, event_type: int) -> None:
        super().__init__()
        self._type = event_type

    ##  The type of event.
    @property
    def type(self) -> int:
        return self._type


##  Mouse Event class.
#   This class represents a mouse event. It has properties corresponding to important mouse
#   event properties and constants for mouse buttons.
class MouseEvent(Event):
    ## Left mouse button.
    LeftButton = "left"
    RightButton = "right"
    MiddleButton = "middle"

    ##  Raise a new mouse event.
    #   \param type The type of event. \sa Event
    #   \param x The X coordinate of the event.
    #   \param y The Y coordinate of the event.
    #   \param last_x The X coordinate of the previous mouse event. Can be None. It is used to calculate deltaX.
    #   \param last_y The Y coordinate of the previous mouse event. Cam be None. It is used to calculate deltaY.
    #   \param buttons The buttons that are associated with this event.
    def __init__(self, event_type: int, x: int = 0, y: int = 0, last_x: int = None, last_y: int = None, buttons: List = None) -> None: #pylint: disable=bad-whitespace
        super().__init__(event_type)
        self._x = x
        self._y = y
        self._last_x = last_x
        self._last_y = last_y
        self._buttons = []  # type: List
        if buttons:
            self._buttons = buttons

    ##  The X coordinate of the event.
    @property
    def x(self) -> int:
        return self._x

    ##  The Y coordinate of the event.
    @property
    def y(self) -> int:
        return self._y

    ##  The X coordinate of the previous event.
    @property
    def lastX(self) -> int:
        return self._last_x

    ##  The Y coordinate of the previous event.
    @property
    def lastY(self) -> int:
        return self._last_y

    ##  The change in X position between this event and the previous event.
    @property
    def deltaX(self) -> int:
        if self._last_x is not None:
            return self._x - self._last_x

        return 0

    ##  The change in Y position between this event and the previous event.
    @property
    def deltaY(self) -> int:
        if self._last_y is not None:
            return self._y - self._last_y

        return 0

    ##  The list of buttons associated with this event.
    @property
    def buttons(self) -> List:
        return self._buttons


##  Event relating to what's happening with the scroll wheel of a mouse.
class WheelEvent(MouseEvent):
    ##  Create a new scroll wheel event.
    #
    #   \param horizontal How far the scroll wheel scrolled horizontally, in
    #   eighths of a degree. To the right is positive. To the left is negative.
    #   \param vertical How far the scroll wheel scrolled vertically, in eighths
    #   of a degree. Up is positive. Down is negative.
    def __init__(self, horizontal: int, vertical: int, x: int = 0, y: int = 0) -> None:
        super().__init__(Event.MouseWheelEvent, x, y)
        self._horizontal = horizontal
        self._vertical = vertical

    ##  How far the scroll wheel was scrolled horizontally, in eighths of a
    #   degree.
    #
    #   To the right is positive. To the left is negative.
    @property
    def horizontal(self) -> int:
        return self._horizontal

    ##  How far the scroll wheel was scrolled vertically, in eighths of a
    #   degree.
    #
    #   Up is positive. Down is negative.
    @property
    def vertical(self) -> int:
        return self._vertical


##  Event regarding the keyboard.
#
#   These events are raised when anything changes in the keyboard state. They
#   keep track of the event type that was given by Qt, for instance whether it
#   was a KeyPressEvent or a KeyReleaseEvent, and they keep track of which key
#   it was.
#
#   Only the special keys are tracked (Shirt, Space, Escape, etc.), not the
#   normal letter keys.
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

    ##  Creates a new key event, passing the event type on to the ``Event``
    #   parent class.
    def __init__(self, event_type: int, key: int) -> None:
        super().__init__(event_type)
        self._key = key

    ##  Which key was pressed.
    #
    #   Compare this with ``KeyEvent.AltKey``, ``KeyEvent.EnterKey``, etc.
    @property
    def key(self) -> int:
        return self._key


##  Tool related event class.
class ToolEvent(Event):
    pass


##  Event used to call a function.
class CallFunctionEvent(Event):
    def __init__(self, func: Callable, args: Any, kwargs: Any) -> None:
        super().__init__(Event.CallFunctionEvent)
        self._function = func
        self._args = args
        self._kwargs = kwargs

    def call(self) -> None:
        self._function(*self._args, **self._kwargs)


##  View related event class.
class ViewEvent(Event):
    pass
