# Copyright (c) 2017 Ultimaker B.V.
# Copyright (c) Thiago Marcos P. Santos
# Copyright (c) Christopher S. Case
# Copyright (c) David H. Bronke
# Uranium is released under the terms of the LGPLv3 or higher.

import enum #For the compress parameter of postponeSignals.
import inspect
import threading
import os
import weakref
from weakref import ReferenceType
from typing import Any, Union, Callable, TypeVar, Generic, List, Tuple, Iterable, cast, Optional
import contextlib
import traceback

import functools

from UM.Event import CallFunctionEvent
from UM.Decorators import call_if_enabled
from UM.Logger import Logger
from UM.Platform import Platform
from UM import FlameProfiler

MYPY = False
if MYPY:
    from UM.Application import Application


# Helper functions for tracing signal emission.
def _traceEmit(signal: Any, *args: Any, **kwargs: Any) -> None:
    Logger.log("d", "Emitting %s with arguments %s", str(signal.getName()), str(args) + str(kwargs))

    if signal._Signal__type == Signal.Queued:
        Logger.log("d", "> Queued signal, postponing emit until next event loop run")

    if signal._Signal__type == Signal.Auto:
        if Signal._signalQueue is not None and threading.current_thread() is not Signal._signalQueue.getMainThread():
            Logger.log("d", "> Auto signal and not on main thread, postponing emit until next event loop run")

    for func in signal._Signal__functions:
        Logger.log("d", "> Calling %s", str(func))

    for dest, func in signal._Signal__methods:
        Logger.log("d", "> Calling %s on %s", str(func), str(dest))

    for signal in signal._Signal__signals:
        Logger.log("d", "> Emitting %s", str(signal._Signal__name))


def _traceConnect(signal: Any, *args: Any, **kwargs: Any) -> None:
    Logger.log("d", "Connecting signal %s to %s", str(signal._Signal__name), str(args[0]))


def _traceDisconnect(signal: Any, *args: Any, **kwargs: Any) -> None:
    Logger.log("d", "Connecting signal %s from %s", str(signal._Signal__name), str(args[0]))


def _isTraceEnabled() -> bool:
    return "URANIUM_TRACE_SIGNALS" in os.environ


class SignalQueue:
    def functionEvent(self, event):
        pass

    def getMainThread(self):
        pass

# Integration with the Flame Profiler.


def _recordSignalNames() -> bool:
    return FlameProfiler.enabled()


def profileEmit(func):
    if FlameProfiler.enabled():
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            FlameProfiler.updateProfileConfig()
            if FlameProfiler.isRecordingProfile():
                with FlameProfiler.profileCall("[SIG] " + self.getName()):
                    func(self, *args, **kwargs)
            else:
                func(self, *args, **kwargs)
        return wrapped

    else:
        return func


class Signal:
    """Simple implementation of signals and slots.

    Signals and slots can be used as a light weight event system. A class can
    define signals that other classes can connect functions or methods to, called slots.
    Whenever the signal is called, it will proceed to call the connected slots.

    To create a signal, create an instance variable of type Signal. Other objects can then
    use that variable's `connect()` method to connect methods, callable objects or signals
    to the signal. To emit the signal, call `emit()` on the signal. Arguments can be passed
    along to the signal, but slots will be required to handle them. When connecting signals
    to other signals, the connected signal will be emitted whenever the signal is emitted.

    Signal-slot connections are weak references and as such will not prevent objects
    from being destroyed. In addition, all slots will be implicitly disconnected when
    the signal is destroyed.

    **WARNING** It is imperative that the signals are created as instance variables, otherwise
    emitting signals will get confused. To help with this, see the SignalEmitter class.

    Loosely based on http://code.activestate.com/recipes/577980-improved-signalsslots-implementation-in-python/    pylint: disable=wrong-spelling-in-comment
    :sa SignalEmitter
    """

    Direct = 1
    """Signal types.
    These indicate the type of a signal, that is, how the signal handles calling the connected
    slots.

    - Direct connections immediately call the connected slots from the thread that called emit().
    - Auto connections will push the call onto the event loop if the current thread is
      not the main thread, but make a direct call if it is.
    - Queued connections will always push
      the call on to the event loop.
    """
    Auto = 2
    Queued = 3

    def __init__(self, type: int = Auto) -> None:
        """Initialize the instance.

        :param type: The signal type. Defaults to Auto.
        """

        # These collections must be treated as immutable otherwise we lose thread safety.
        self.__functions = WeakImmutableList()      # type: WeakImmutableList[Callable[[], None]]
        self.__methods = WeakImmutablePairList()    # type: WeakImmutablePairList[Any, Callable[[], None]]
        self.__signals = WeakImmutableList()        # type: WeakImmutableList[Signal]

        self.__lock = threading.Lock()  # Guards access to the fields above.
        self.__type = type

        self._postpone_emit = False
        self._postpone_thread = None    # type: Optional[threading.Thread]
        self._compress_postpone = False # type: bool
        self._postponed_emits = None    # type: Any

        if _recordSignalNames():
            try:
                if Platform.isWindows():
                    self.__name = inspect.stack()[1][0].f_locals["key"]
                else:
                    self.__name = inspect.stack()[1].frame.f_locals["key"]
            except KeyError:
                self.__name = "Signal"
        else:
            self.__name = "Anon"

    def getName(self):
        return self.__name

    def __call__(self) -> None:
        """:exception NotImplementedError:"""

        raise NotImplementedError("Call emit() to emit a signal")

    def getType(self) -> int:
        """Get type of the signal

        :return: Direct(1), Auto(2) or Queued(3)
        """

        return self.__type

    @call_if_enabled(_traceEmit, _isTraceEnabled())
    @profileEmit
    def emit(self, *args: Any, **kwargs: Any) -> None:
        """Emit the signal which indirectly calls all of the connected slots.

        :param args: The positional arguments to pass along.
        :param kwargs: The keyword arguments to pass along.

        :note If the Signal type is Queued and this is not called from the application thread
        the call will be posted as an event to the application main thread, which means the
        function will be called on the next application event loop tick.
        """

        # Check to see if we need to postpone emits
        if self._postpone_emit:
            if threading.current_thread() != self._postpone_thread:
                Logger.log("w", "Tried to emit signal from thread %s while emits are being postponed by %s. Traceback:", threading.current_thread(), self._postpone_thread)
                tb = traceback.format_stack()
                for line in tb:
                    Logger.log("w", line)

            if self._compress_postpone == CompressTechnique.CompressSingle:
                # If emits should be compressed, we only emit the last emit that was called
                self._postponed_emits = (args, kwargs)
            else:
                # If emits should not be compressed or compressed per parameter value, we catch all calls to emit and put them in a list to be called later.
                if not self._postponed_emits:
                    self._postponed_emits = []
                self._postponed_emits.append((args, kwargs))
            return

        try:
            if self.__type == Signal.Queued:
                Signal._app.functionEvent(CallFunctionEvent(self.__performEmit, args, kwargs))
                return
            if self.__type == Signal.Auto:
                if threading.current_thread() is not Signal._app.getMainThread():
                    Signal._app.functionEvent(CallFunctionEvent(self.__performEmit, args, kwargs))
                    return
        except AttributeError: # If Signal._app is not set
            return

        self.__performEmit(*args, **kwargs)

    @call_if_enabled(_traceConnect, _isTraceEnabled())
    def connect(self, connector: Union["Signal", Callable[[], None]]) -> None:
        """Connect to this signal.

        :param connector: The signal or slot (function) to connect.
        """

        if self._postpone_emit:
            Logger.log("w", "Tried to connect to signal %s that is currently being postponed, this is not possible", self.__name)
            return

        with self.__lock:
            if isinstance(connector, Signal):
                if connector == self:
                    return
                self.__signals = self.__signals.append(connector)
            elif inspect.ismethod(connector):
                # if SIGNAL_PROFILE:
                #     Logger.log('d', "Connector method qual name: " + connector.__func__.__qualname__)
                self.__methods = self.__methods.append(cast(Any, connector).__self__, cast(Any, connector).__func__)
            else:
                # Once again, update the list of functions using a whole new list.
                # if SIGNAL_PROFILE:
                #     Logger.log('d', "Connector function qual name: " + connector.__qualname__)

                self.__functions = self.__functions.append(connector)

    @call_if_enabled(_traceDisconnect, _isTraceEnabled())
    def disconnect(self, connector):
        """Disconnect from this signal.

        :param connector: The signal or slot (function) to disconnect.
        """

        if self._postpone_emit:
            Logger.log("w", "Tried to disconnect from signal %s that is currently being postponed, this is not possible", self.__name)
            return

        with self.__lock:
            if isinstance(connector, Signal):
                self.__signals = self.__signals.remove(connector)
            elif inspect.ismethod(connector):
                self.__methods = self.__methods.remove(connector.__self__, connector.__func__)
            else:
                self.__functions = self.__functions.remove(connector)

    def disconnectAll(self):
        """Disconnect all connected slots."""

        if self._postpone_emit:
            Logger.log("w", "Tried to disconnect from signal %s that is currently being postponed, this is not possible", self.__name)
            return

        with self.__lock:
            self.__functions = WeakImmutableList()      # type: "WeakImmutableList"
            self.__methods = WeakImmutablePairList()    # type: "WeakImmutablePairList"
            self.__signals = WeakImmutableList()        # type: "WeakImmutableList"

    def __getstate__(self):
        """To support Pickle

        Since Weak containers cannot be serialized by Pickle we just return an empty dict as state.
        """

        return {}

    def __deepcopy__(self, memo):
        """To properly handle deepcopy in combination with __getstate__

        Apparently deepcopy uses __getstate__ internally, which is not documented. The reimplementation
        of __getstate__ then breaks deepcopy. On the other hand, if we do not reimplement it like that,
        we break pickle. So instead make sure to also reimplement __deepcopy__.
        """

        # Snapshot these fields
        with self.__lock:
            functions = self.__functions
            methods = self.__methods
            signals = self.__signals

        signal = Signal(type = self.__type)
        signal.__functions = functions
        signal.__methods = methods
        signal.__signals = signals
        return signal

    _app = None  # type: Application
    """To avoid circular references when importing Application, this should be
    set by the Application instance.
    """

    _signalQueue = None  # type: Application

    # Private implementation of the actual emit.
    # This is done to make it possible to freely push function events without needing to maintain state.
    def __performEmit(self, *args, **kwargs) -> None:
        # Quickly make some private references to the collections we need to process.
        # Although the these fields are always safe to use read and use with regards to threading,
        # we want to operate on a consistent snapshot of the whole set of fields.
        with self.__lock:
            functions = self.__functions
            methods = self.__methods
            signals = self.__signals

        if not FlameProfiler.isRecordingProfile():
            # Call handler functions
            for func in functions:
                func(*args, **kwargs)

            # Call handler methods
            for dest, func in methods:
                func(dest, *args, **kwargs)

            # Emit connected signals
            for signal in signals:
                signal.emit(*args, **kwargs)
        else:
            # Call handler functions
            for func in functions:
                with FlameProfiler.profileCall(func.__qualname__):
                    func(*args, **kwargs)

            # Call handler methods
            for dest, func in methods:
                with FlameProfiler.profileCall(func.__qualname__):
                    func(dest, *args, **kwargs)

            # Emit connected signals
            for signal in signals:
                with FlameProfiler.profileCall("[SIG]" + signal.getName()):
                    signal.emit(*args, **kwargs)

    # This __str__() is useful for debugging.
    # def __str__(self):
    #     function_str = ", ".join([repr(f) for f in self.__functions])
    #     method_str = ", ".join([ "{dest: " + str(dest) + ", funcs: " + strMethodSet(funcs) + "}" for dest, funcs in self.__methods])
    #     signal_str = ", ".join([str(signal) for signal in self.__signals])
    #     return "Signal<{}> {{ __functions={{ {} }}, __methods={{ {} }}, __signals={{ {} }} }}".format(id(self), function_str, method_str, signal_str)


#def strMethodSet(method_set):
#    return "{" + ", ".join([str(m) for m in method_set]) + "}"


class CompressTechnique(enum.Enum):
    NoCompression = 0
    CompressSingle = 1
    CompressPerParameterValue = 2

@contextlib.contextmanager
def postponeSignals(*signals, compress: CompressTechnique = CompressTechnique.NoCompression):
    """A context manager that allows postponing of signal emissions

    This context manager will collect any calls to emit() made for the provided signals
    and only emit them after exiting. This ensures more batched processing of signals.

    The optional "compress" argument will limit the emit calls to 1. This means that
    when a bunch of calls are made to the signal's emit() method, only the last call
    will be emitted on exit.

    **WARNING** When compress is True, only the **last** call will be emitted. This means
    that any other calls will be ignored, _including their arguments_.

    :param signals: The signals to postpone emits for.
    :param compress: Whether to enable compression of emits or not.
    """

    # To allow for nested postpones on the same signals, we should check if signals are not already
    # postponed and only change those that are not yet postponed.
    restore_emit = []
    for signal in signals:
        if not signal._postpone_emit: # Do nothing if the signal has already been changed
            signal._postpone_emit = True
            signal._postpone_thread = threading.current_thread()
            signal._compress_postpone = compress
            # Since we made changes, make sure to restore the signal after exiting the context manager
            restore_emit.append(signal)

    # Execute the code block in the "with" statement
    yield

    for signal in restore_emit:
        # We are done with the code, restore all changed signals to their "normal" state
        signal._postpone_emit = False

        if signal._postponed_emits:
            # Send any signal emits that were collected while emits were being postponed
            if signal._compress_postpone == CompressTechnique.CompressSingle:
                signal.emit(*signal._postponed_emits[0], **signal._postponed_emits[1])
            elif signal._compress_postpone == CompressTechnique.CompressPerParameterValue:
                uniques = {(tuple(args), tuple(kwargs.items())) for args, kwargs in signal._postponed_emits} #Have to make them tuples in order to make them hashable.
                for args, kwargs in uniques:
                    signal.emit(*args, **dict(kwargs))
            else:
                for args, kwargs in signal._postponed_emits:
                    signal.emit(*args, **kwargs)
            signal._postponed_emits = None

        signal._postpone_thread = None
        signal._compress_postpone = False


def signalemitter(cls):
    """Class decorator that ensures a class has unique instances of signals.

    Since signals need to be instance variables, normally you would need to create all
    signals in the class" `__init__` method. However, this makes them rather awkward to
    document. This decorator instead makes it possible to declare them as class variables,
    which makes documenting them near the function they are used possible. This decorator
    adjusts the class' __new__ method to create new signal instances for all class signals.
    """

    # First, check if the base class has any signals defined
    signals = inspect.getmembers(cls, lambda i: isinstance(i, Signal))
    if not signals:
        raise TypeError("Class {0} is marked as signal emitter but no signal were found".format(cls))

    # Then, replace the class' new method with one that modifies the created instance to have
    # unique signals.
    old_new = cls.__new__
    def new_new(subclass, *args, **kwargs):
        if old_new == object.__new__:
            sub = object.__new__(subclass)
        else:
            sub = old_new(subclass, *args, **kwargs)

        for key, value in inspect.getmembers(cls, lambda i: isinstance(i, Signal)):
            setattr(sub, key, Signal(type = value.getType()))

        return sub

    cls.__new__ = new_new
    return cls


T = TypeVar('T')


class WeakImmutableList(Generic[T], Iterable):
    """Minimal implementation of a weak reference list with immutable tendencies.

    Strictly speaking this isn't immutable because the garbage collector can modify
    it, but no application code can. Also, this class doesn't implement the Python
    list API, only the handful of methods we actually need in the code above.
    """

    def __init__(self) -> None:
        self.__list = []    # type: List[ReferenceType[Optional[T]]]

    def append(self, item: T) -> "WeakImmutableList[T]":
        """Append an item and return a new list

        :param item: the item to append
        :return: a new list
        """

        new_instance = WeakImmutableList()  # type: WeakImmutableList[T]
        new_instance.__list = self.__cleanList()
        new_instance.__list.append(ReferenceType(item))
        return new_instance

    def remove(self, item: T) -> "WeakImmutableList[T]":
        """Remove an item and return a list

        Note that unlike the normal Python list.remove() method, this ones
        doesn't throw a ValueError if the item isn't in the list.
        :param item: item to remove
        :return: a list which does not have the item.
        """

        for item_ref in self.__list:
            if item_ref() is item:
                new_instance = WeakImmutableList()   # type: WeakImmutableList[T]
                new_instance.__list = self.__cleanList()
                new_instance.__list.remove(item_ref)
                return new_instance
        else:
            return self  # No changes needed

    # Create a new list with the missing values removed.
    def __cleanList(self) -> "List[ReferenceType[Optional[T]]]":
        return [item_ref for item_ref in self.__list if item_ref() is not None]

    def __iter__(self):
        return WeakImmutableListIterator(self.__list)


class WeakImmutableListIterator(Generic[T], Iterable):
    """Iterator wrapper which filters out missing values.

    It dereferences each weak reference object and filters out the objects
    which have already disappeared via GC.
    """

    def __init__(self, list_):
        self.__it = list_.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        next_item = self.__it.__next__()()
        while next_item is None:    # Skip missing values
            next_item = self.__it.__next__()()
        return next_item


U = TypeVar('U')


class WeakImmutablePairList(Generic[T, U], Iterable):
    """A variation of WeakImmutableList which holds a pair of values using weak refernces."""

    def __init__(self) -> None:
        self.__list = []    # type: List[Tuple[ReferenceType[T],ReferenceType[U]]]

    def append(self, left_item: T, right_item: U) -> "WeakImmutablePairList[T,U]":
        """Append an item and return a new list

        :param item: the item to append
        :return: a new list
        """

        new_instance = WeakImmutablePairList()  # type: WeakImmutablePairList[T,U]
        new_instance.__list = self.__cleanList()
        new_instance.__list.append( (weakref.ref(left_item), weakref.ref(right_item)) )
        return new_instance

    def remove(self, left_item: T, right_item: U) -> "WeakImmutablePairList[T,U]":
        """Remove an item and return a list

        Note that unlike the normal Python list.remove() method, this ones
        doesn't throw a ValueError if the item isn't in the list.
        :param item: item to remove
        :return: a list which does not have the item.
        """

        for pair in self.__list:
            left = pair[0]()
            right = pair[1]()

            if left is left_item and right is right_item:
                new_instance = WeakImmutablePairList() # type: WeakImmutablePairList[T,U]
                new_instance.__list = self.__cleanList()
                new_instance.__list.remove(pair)
                return new_instance
        else:
            return self # No changes needed

    # Create a new list with the missing values removed.
    def __cleanList(self) -> List[Tuple[ReferenceType,ReferenceType]]:
        return [pair for pair in self.__list if pair[0]() is not None and pair[1]() is not None]

    def __iter__(self):
        return WeakImmutablePairListIterator(self.__list)


# A small iterator wrapper which dereferences the weak ref objects and filters
# out the objects which have already disappeared via GC.
class WeakImmutablePairListIterator:
    def __init__(self, list_) -> None:
        self.__it = list_.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        pair = self.__it.__next__()
        left = pair[0]()
        right = pair[1]()
        while left is None or right is None:    # Skip missing values
            pair = self.__it.__next__()
            left = pair[0]()
            right = pair[1]()

        return left, right
