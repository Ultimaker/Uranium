# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

##  \file Event.py
#   Contains the Event class and important subclasses used throughout UM.


##  Base event class.
#   Defines the most basic interface for events and several constants to identify event types.
from typing import List, Any, Callable, Optional


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

    @property
    def type(self) -> int:
        """The type of event."""

        return self._type


class MouseEvent(Event):
    """Mouse Event class.

    This class represents a mouse event. It has properties corresponding to important mouse
    event properties and constants for mouse buttons.
    """

    LeftButton = "left"
    """Left mouse button."""
    RightButton = "right"
    MiddleButton = "middle"

    def __init__(self, event_type: int, x: int = 0, y: int = 0, last_x: int = None, last_y: int = None, buttons: List[str] = None) -> None: #pylint: disable=bad-whitespace
        """Raise a new mouse event.

        :param event_type: The type of event. :sa Event
        :param x: The X coordinate of the event.
        :param y: The Y coordinate of the event.
        :param last_x: The X coordinate of the previous mouse event. Can be None. It is used to calculate deltaX.
        :param last_y: The Y coordinate of the previous mouse event. Cam be None. It is used to calculate deltaY.
        :param buttons: The buttons that are associated with this event.
        """

        super().__init__(event_type)
        self._x = x
        self._y = y
        self._last_x = last_x
        self._last_y = last_y
        self._buttons = []  # type: List[str]
        if buttons:
            self._buttons = buttons

    @property
    def x(self) -> int:
        """The X coordinate of the event."""

        return self._x

    @property
    def y(self) -> int:
        """The Y coordinate of the event."""

        return self._y

    @property
    def lastX(self) -> Optional[int]:
        """The X coordinate of the previous event."""

        return self._last_x

    @property
    def lastY(self) -> Optional[int]:
        """The Y coordinate of the previous event."""

        return self._last_y

    @property
    def deltaX(self) -> int:
        """The change in X position between this event and the previous event."""

        if self._last_x is not None:
            return self._x - self._last_x

        return 0

    @property
    def deltaY(self) -> int:
        """The change in Y position between this event and the previous event."""

        if self._last_y is not None:
            return self._y - self._last_y

        return 0

    @property
    def buttons(self) -> List[str]:
        """The list of buttons associated with this event."""

        return self._buttons


class WheelEvent(MouseEvent):
    """Event relating to what's happening with the scroll wheel of a mouse."""

    def __init__(self, horizontal: int, vertical: int, x: int = 0, y: int = 0) -> None:
        """Create a new scroll wheel event.

        :param horizontal: How far the scroll wheel scrolled horizontally, in
               eighths of a degree. To the right is positive. To the left is negative.
        :param vertical: How far the scroll wheel scrolled vertically, in eighths
               of a degree. Up is positive. Down is negative.
        """

        super().__init__(Event.MouseWheelEvent, x, y)
        self._horizontal = horizontal
        self._vertical = vertical

    @property
    def horizontal(self) -> int:
        """How far the scroll wheel was scrolled horizontally, in eighths of a
        degree.

        To the right is positive. To the left is negative.
        """

        return self._horizontal

    @property
    def vertical(self) -> int:
        """How far the scroll wheel was scrolled vertically, in eighths of a
        degree.

        Up is positive. Down is negative.
        """

        return self._vertical


class KeyEvent(Event):
    """Event regarding the keyboard.

    These events are raised when anything changes in the keyboard state. They
    keep track of the event type that was given by Qt, for instance whether it
    was a KeyPressEvent or a KeyReleaseEvent, and they keep track of which key
    it was.

    Only the special keys are tracked (Shirt, Space, Escape, etc.), not the
    normal letter keys.
    """

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

    def __init__(self, event_type: int, key: int) -> None:
        """Creates a new key event, passing the event type on to the `Event`
        parent class.
        """

        super().__init__(event_type)
        self._key = key

    @property
    def key(self) -> int:
        """Which key was pressed.

        Compare this with `KeyEvent.AltKey`, `KeyEvent.EnterKey`, etc.
        """

        return self._key


class ToolEvent(Event):
    """Tool related event class."""

    pass


class CallFunctionEvent(Event):
    """Event used to call a function."""

    def __init__(self, func: Callable[..., Any], args: Any, kwargs: Any) -> None:
        super().__init__(Event.CallFunctionEvent)
        self._function = func
        self._args = args
        self._kwargs = kwargs

    def call(self) -> None:
        self._function(*self._args, **self._kwargs)


class ViewEvent(Event):
    """View related event class."""

    pass
