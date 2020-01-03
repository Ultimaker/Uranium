# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Callable, Dict, Optional, cast

from PyQt5.QtCore import QObject, QCoreApplication, QEvent, QTimer


__all__ = ["TaskManager"]


#
# A custom event that's used to store a callback function and its parameters. When this event is handled, the handling
# object should invoke the callFunction() method so the callback function will be invoked.
#
class _CallFunctionEvent(QEvent):

    def __init__(self, task_manager: "TaskManager", func: Callable, args: Any, kwargs: Any,
                 delay: Optional[float] = None) -> None:
        super().__init__(task_manager.event_type)

        self._task_manager = task_manager
        self._function = func
        self._args = args
        self._kwargs = kwargs
        self._delay = delay

    @property
    def delay(self) -> Optional[float]:
        return self._delay

    def callFunction(self) -> None:
        self._function(*self._args, **self._kwargs)


#
#
# This is not a singleton class. The TaskManager is intended to make it easier for certain task-management-ish classes
# to handle tasks within the Qt event loop framework. It makes it easier to:
#
#  - Schedule a callback that will be picked up by the Qt event loop later.
#  - Schedule a callback with a delay (given in seconds).
#  - Remove all callbacks that has been scheduled but not yet invoked.
#
# This class uses QEvent, unique QEvent types, and QCoreApplication::postEvent() to achieve those functionality. A
# unique QEvent type is assigned for each TaskManager instance, so each instance can cancel the QEvent posted by itself.
# The unique QEvent type is retrieved via QEvent.registerEventType(), which will return a unique custom event type if
# available. If no more custom event type is available, it will return -1. A custom/user event type is a number between
# QEvent::User (1000) and QEvent::MaxUser (65535). See https://doc.qt.io/qt-5/qevent.html
#
# Here we use QCoreApplication.removePostedEvents() to remove posted but not yet dispatched events. Those are the events
# that have been posted but not yet processed. You can consider this as cancelling a task that you have scheduled
# earlier but it has not yet been executed. Because QCoreApplication.removePostedEvents() can use an eventType argument
# to specify the event type you want to remove, here we use that unique custom event type for each TaskManager to
# identify all events that are managed by the TaskManager itself. See https://doc.qt.io/qt-5/qcoreapplication.html
#
# According to my experience, QTimer doesn't seem to trigger events very accurately. I had for example, an expected
# delay of 5.0 seconds, but I got an actual delay of 4.7 seconds. That's around 6% off. So, here we add a little
# tolerance to all the specified delay.
#
class TaskManager(QObject):

    TIME_TOLERANCE = 0.10  # Add 10% to the delayed events to compensate for timer inaccuracy.

    # Acquires a new unique Qt event type integer.
    @staticmethod
    def acquireNewEventType() -> int:
        # QCoreApplication.registerEventType() is thread-safe.
        new_type = QEvent.registerEventType()
        if new_type == -1:
            raise RuntimeError("Failed to register new event type. All user event types are already taken.")
        return new_type

    def __init__(self, parent: Optional["QObject"]) -> None:
        super().__init__(parent = parent)
        self._event_type = TaskManager.acquireNewEventType()
        # For storing all delayed events
        self._delayed_events = dict()  # type: Dict[_CallFunctionEvent, Dict[str, Any]]

    @property
    def event_type(self) -> int:
        return self._event_type

    # Cleans up all the delayed events and remove all events that were posted by this TaskManager instance.
    def cleanup(self) -> None:
        for event in list(self._delayed_events.keys()):
            self._cleanupDelayedCallEvent(event)
        self._delayed_events.clear()

        # Removes all events that have been posted to the QApplication.
        QCoreApplication.instance().removePostedEvents(None, self._event_type)

    # Schedules a callback function to be called later. If delay is given, the callback will be scheduled to call after
    # the given amount of time. Otherwise, the callback will be scheduled to the QCoreApplication instance to be called
    # the next time the event gets picked up.
    def callLater(self, delay: float, callback: Callable, *args, **kwargs) -> None:
        if delay < 0:
            raise ValueError("delay must be a non-negative value, but got [%s] instead." % delay)

        delay_to_use = None if delay <= 0 else delay
        event = _CallFunctionEvent(self, callback, args, kwargs,
                                   delay = delay_to_use)
        if delay_to_use is None:
            QCoreApplication.instance().postEvent(self, event)
        else:
            self._scheduleDelayedCallEvent(event)

    def _scheduleDelayedCallEvent(self, event: "_CallFunctionEvent") -> None:
        if event.delay is None:
            return

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(event.delay * 1000 * (1 + self.TIME_TOLERANCE))
        timer_callback = lambda e = event: self._onDelayReached(e)
        timer.timeout.connect(timer_callback)
        timer.start()
        self._delayed_events[event] = {"event": event,
                                       "timer": timer,
                                       "timer_callback": timer_callback,
                                       }

    def _cleanupDelayedCallEvent(self, event: "_CallFunctionEvent") -> None:
        info_dict = self._delayed_events.get(event)
        if info_dict is None:
            return

        timer_callback = info_dict["timer_callback"]
        timer = info_dict["timer"]
        timer.stop()
        timer.timeout.disconnect(timer_callback)

        del self._delayed_events[event]

    def _onDelayReached(self, event: "_CallFunctionEvent") -> None:
        QCoreApplication.instance().postEvent(self, event)

    # Handle Qt events
    def event(self, event: "QEvent") -> bool:
        # Call the function
        if event.type() == self._event_type:
            call_event = cast(_CallFunctionEvent, event)
            call_event.callFunction()
            self._cleanupDelayedCallEvent(call_event)
            return True

        return super().event(event)
