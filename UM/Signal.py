# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) Thiago Marcos P. Santos
# Copyright (c) Christopher S. Case
# Copyright (c) David H. Bronke
# Uranium is released under the terms of the AGPLv3 or higher.

import inspect
import threading
import os
import weakref

from UM.Event import CallFunctionEvent
from UM.Decorators import deprecated, call_if_enabled
from UM.Logger import Logger
from UM.Platform import Platform

# Helper functions for tracing signal emission.
def _traceEmit(signal, *args, **kwargs):
    Logger.log("d", "Emitting %s with arguments %s", str(signal._Signal__name), str(args) + str(kwargs))

    if signal._Signal__type == Signal.Queued:
        Logger.log("d", "> Queued signal, postponing emit until next event loop run")

    if signal._Signal__type == Signal.Auto:
        if Signal._app is not None and threading.current_thread() is not Signal._app.getMainThread():
            Logger.log("d", "> Auto signal and not on main thread, postponing emit until next event loop run")

    for func in signal._Signal__functions:
        Logger.log("d", "> Calling %s", str(func))

    for dest, func in signal._Signal__methods:
        Logger.log("d", "> Calling %s on %s", str(func), str(dest))

    for signal in signal._Signal__signals:
        Logger.log("d", "> Emitting %s", str(signal._Signal__name))


def _traceConnect(signal, *args, **kwargs):
    Logger.log("d", "Connecting signal %s to %s", str(signal._Signal__name), str(args[0]))

def _traceDisconnect(signal, *args, **kwargs):
    Logger.log("d", "Connecting signal %s from %s", str(signal._Signal__name), str(args[0]))

def _isTraceEnabled():
    return "URANIUM_TRACE_SIGNALS" in os.environ

##  Simple implementation of signals and slots.
#
#   Signals and slots can be used as a light weight event system. A class can
#   define signals that other classes can connect functions or methods to, called slots.
#   Whenever the signal is called, it will proceed to call the connected slots.
#
#   To create a signal, create an instance variable of type Signal. Other objects can then
#   use that variable's `connect()` method to connect methods, callable objects or signals
#   to the signal. To emit the signal, call `emit()` on the signal. Arguments can be passed
#   along to the signal, but slots will be required to handle them. When connecting signals
#   to other signals, the connected signal will be emitted whenever the signal is emitted.
#
#   Signal-slot connections are weak references and as such will not prevent objects
#   from being destroyed. In addition, all slots will be implicitly disconnected when
#   the signal is destroyed.
#
#   \warning It is imperative that the signals are created as instance variables, otherwise
#   emitting signals will get confused. To help with this, see the SignalEmitter class.
#
#   Loosely based on http://code.activestate.com/recipes/577980-improved-signalsslots-implementation-in-python/ #pylint: disable=wrong-spelling-in-comment
#   \sa SignalEmitter
class Signal:
    ##  Signal types.
    #   These indicate the type of a signal, that is, how the signal handles calling the connected
    #   slots.
    #   - Direct connections immediately call the connected slots from the thread that called emit().
    #   - Auto connections will push the call onto the event loop if the current thread is
    #     not the main thread, but make a direct call if it is.
    #   - Queued connections will always push
    #     the call on to the event loop.
    Direct = 1
    Auto = 2
    Queued = 3

    ##  Initialize the instance.
    #
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - type: The signal type. Defaults to Auto.
    def __init__(self, **kwargs):
        # These collections must be treated as immutable otherwise we lose thread safety.
        self.__functions = WeakImmutableList()
        self.__methods = WeakImmutablePairList()
        self.__signals = WeakImmutableList()

        self.__lock = threading.Lock()  # Guards access to the fields above.

        self.__type = kwargs.get("type", Signal.Auto)

        if "URANIUM_TRACE_SIGNALS" in os.environ:
            try:
                if Platform.isWindows():
                    self.__name = inspect.stack()[1][0].f_locals["key"]
                else:
                    self.__name = inspect.stack()[1].frame.f_locals["key"]
            except KeyError:
                self.__name = "Signal"

    ##  \exception NotImplementedError
    def __call__(self):
        raise NotImplementedError("Call emit() to emit a signal")

    ##  Get type of the signal
    #   \return \type{int} Direct(1), Auto(2) or Queued(3)
    def getType(self):
        return self.__type

    ##  Emit the signal which indirectly calls all of the connected slots.
    #
    #   \param args The positional arguments to pass along.
    #   \param kwargs The keyword arguments to pass along.
    #
    #   \note If the Signal type is Queued and this is not called from the application thread
    #   the call will be posted as an event to the application main thread, which means the
    #   function will be called on the next application event loop tick.
    @call_if_enabled(_traceEmit, _isTraceEnabled())
    def emit(self, *args, **kwargs):
        try:
            if self.__type == Signal.Queued:
                Signal._app.functionEvent(CallFunctionEvent(self.emit, args, kwargs))
                return

            if self.__type == Signal.Auto:
                if threading.current_thread() is not Signal._app.getMainThread():
                    Signal._app.functionEvent(CallFunctionEvent(self.emit, args, kwargs))
                    return
        except AttributeError: # If Signal._app is not set
            return

        # Quickly make some private references to the collections we need to process.
        # Although the these fields are always safe to use read and use with regards to threading,
        # we want to operate on a consistent snapshot of the whole set of fields.
        with self.__lock:
            functions = self.__functions
            methods = self.__methods
            signals = self.__signals

        # Call handler functions
        for func in functions:
            func(*args, **kwargs)

        # Call handler methods
        for dest, func in methods:
            func(dest, *args, **kwargs)

        # Emit connected signals
        for signal in signals:
            signal.emit(*args, **kwargs)

    ##  Connect to this signal.
    #   \param connector The signal or slot (function) to connect.
    @call_if_enabled(_traceConnect, _isTraceEnabled())
    def connect(self, connector):
        with self.__lock:
            if isinstance(connector, Signal):
                if connector == self:
                    return
                self.__signals = self.__signals.append(connector)
            elif inspect.ismethod(connector):
                self.__methods = self.__methods.append(connector.__self__, connector.__func__)
            else:
                # Once again, update the list of functions using a whole new list.
                self.__functions = self.__functions.append(connector)

    ##  Disconnect from this signal.
    #   \param connector The signal or slot (function) to disconnect.
    @call_if_enabled(_traceDisconnect, _isTraceEnabled())
    def disconnect(self, connector):
        with self.__lock:
            if isinstance(connector, Signal):
                self.__signals = self.__signals.remove(connector)
            elif inspect.ismethod(connector):
                self.__methods = self.__methods.remove(connector.__self__, connector.__func__)
            else:
                self.__functions = self.__functions.remove(connector)

    ##  Disconnect all connected slots.
    def disconnectAll(self):
        with self.__lock:
            self.__functions = WeakImmutableList()
            self.__methods = WeakImmutablePairList()
            self.__signals = WeakImmutableList()

    ##  To support Pickle
    #
    #   Since Weak containers cannot be serialized by Pickle we just return an empty dict as state.
    def __getstate__(self):
        return {}

    ##  To proerly handle deepcopy in combination with __getstate__
    #
    #   Apparently deepcopy uses __getstate__ internally, which is not documented. The reimplementation
    #   of __getstate__ then breaks deepcopy. On the other hand, if we do not reimplement it like that,
    #   we break pickle. So instead make sure to also reimplement __deepcopy__.
    def __deepcopy__(self, memo):
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

    ##  private:

    #   To avoid circular references when importing Application, this should be
    #   set by the Application instance.
    _app = None

    # This __str__() is useful for debugging.
    # def __str__(self):
    #     function_str = ", ".join([repr(f) for f in self.__functions])
    #     method_str = ", ".join([ "{dest: " + str(dest) + ", funcs: " + strMethodSet(funcs) + "}" for dest, funcs in self.__methods])
    #     signal_str = ", ".join([str(signal) for signal in self.__signals])
    #     return "Signal<{}> {{ __functions={{ {} }}, __methods={{ {} }}, __signals={{ {} }} }}".format(id(self), function_str, method_str, signal_str)

def strMethodSet(method_set):
    return "{" + ", ".join([str(m) for m in method_set]) + "}"

##  Convenience class to simplify signal creation.
#
#   This class is a Convenience class to simplify signal creation. Since signals
#   need to be instance variables, normally you would need to create all signals
#   in the class" `__init__` method. However, this makes them rather awkward to
#   document. This class instead makes it possible to declare them as class variables,
#   which makes documenting them near the function they are used possible.
#   During the call to `__init__()`, this class will then search through all the
#   properties of the instance and create instance variables for each class variable
#   that is an instance of Signal.
class SignalEmitter:
    ##  Initialize method.
    @deprecated("Please use the new @signalemitter decorator", "2.2")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for name, signal in inspect.getmembers(self, lambda i: isinstance(i, Signal)):
            setattr(self, name, Signal(type = signal.getType())) #pylint: disable=bad-whitespace

##  Class decorator that ensures a class has unique instances of signals.
#
#   Since signals need to be instance variables, normally you would need to create all
#   signals in the class" `__init__` method. However, this makes them rather awkward to
#   document. This decorator instead makes it possible to declare them as class variables,
#   which makes documenting them near the function they are used possible. This decorator
#   adjusts the class' __new__ method to create new signal instances for all class signals.
def signalemitter(cls):
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

##  Minimal implementation of a weak reference list with immutable tendencies.
#
#   Strictly speaking this isn't immutable because the garbage collector can modify
#   it, but no application code can. Also, this class doesn't implement the Python
#   list API, only the handful of methods we actually need in the code above.
class WeakImmutableList:
    def __init__(self):
        self.__list = []

    ## Append an item and return a new list
    #
    #  \param item the item to append
    #  \return a new list
    def append(self, item):
        new_instance = WeakImmutableList()
        new_instance.__list = self.__cleanList()
        new_instance.__list.append(weakref.ref(item))
        return new_instance

    ## Remove an item and return a list
    #
    #  Note that unlike the normal Python list.remove() method, this ones
    #  doesn't throw a ValueError if the item isn't in the list.
    #  \param item item to remove
    #  \return a list which does not have the item.
    def remove(self, item):
        for item_ref in self.__list:
            if item_ref() is item:
                new_instance = WeakImmutableList()
                new_instance.__list = self.__cleanList()
                new_instance.__list.remove(item_ref)
                return new_instance
        else:
            return self # No changes needed

    # Create a new list with the missing values removed.
    def __cleanList(self):
        return [item_ref for item_ref in self.__list if item_ref() is not None]

    def __iter__(self):
        return WeakImmutableListIterator(self.__list)

## Iterator wrapper which filters out missing values.
#
# It dereferences each weak reference object and filters out the objects
# which have already disappeared via GC.
class WeakImmutableListIterator:
    def __init__(self, list_):
        self.__it = list_.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        next_item = self.__it.__next__()()
        while next_item is None:    # Skip missing values
            next_item = self.__it.__next__()()
        return next_item

##  A variation of WeakImmutableList which holds a pair of values using weak refernces.
class WeakImmutablePairList:
    def __init__(self):
        self.__list = []

    ## Append an item and return a new list
    #
    #  \param item the item to append
    #  \return a new list
    def append(self, left_item, right_item):
        new_instance = WeakImmutablePairList()
        new_instance.__list = self.__cleanList()
        new_instance.__list.append( (weakref.ref(left_item), weakref.ref(right_item)) )
        return new_instance

    ## Remove an item and return a list
    #
    #  Note that unlike the normal Python list.remove() method, this ones
    #  doesn't throw a ValueError if the item isn't in the list.
    #  \param item item to remove
    #  \return a list which does not have the item.
    def remove(self, left_item, right_item):
        for pair in self.__list:
            left = pair[0]()
            right = pair[1]()

            if left is left_item and right is right_item:
                new_instance = WeakImmutablePairList()
                new_instance.__list = self.__cleanList()
                new_instance.__list.remove(pair)
                return new_instance
        else:
            return self # No changes needed

    # Create a new list with the missing values removed.
    def __cleanList(self):
        return [pair for pair in self.__list if pair[0]() is not None and pair[1]() is not None]

    def __iter__(self):
        return WeakImmutablePairListIterator(self.__list)

# A small iterator wrapper which dereferences the weak ref objects and filters
# out the objects which have already disappeared via GC.
class WeakImmutablePairListIterator:
    def __init__(self, list_):
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

        return (left, right)
