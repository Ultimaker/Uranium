# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) Thiago Marcos P. Santos
# Copyright (c) Christopher S. Case
# Copyright (c) David H. Bronke
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Event import CallFunctionEvent

import inspect
import threading
from weakref import WeakSet, WeakKeyDictionary


##  Simple implementation of signals and slots.
#
#   Signals and slots can be used as a light weight event system. A class can
#   define signals that other classes can connect functions or methods to, called slots.
#   Whenever the signal is called, it will proceed to call the connected slots.
#
#   To create a signal, create an instance variable of type Signal. Other objects can then
#   use that variable"s `connect()` method to connect methods, callables or signals to the
#   signal. To emit the signal, call `emit()` on the signal. Arguments can be passed along
#   to the signal, but slots will be required to handle them. When connecting signals to
#   other signals, the connected signal will be emitted whenever the signal is emitted.
#
#   Signal-slot connections are weak references and as such will not prevent objects
#   from being destroyed. In addition, all slots will be implicitly disconnected when
#   the signal is destroyed.
#
#   \warning It is imperative that the signals are created as instance variables, otherwise
#   emitting signals will get confused. To help with this, see the SignalEmitter class.
#
#   Loosely based on http://code.activestate.com/recipes/577980-improved-signalsslots-implementation-in-python/
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
    #                 - type: The signal type. Defaults to Direct.
    def __init__(self, **kwargs):
        self.__functions = WeakSet()
        self.__methods = WeakKeyDictionary()
        self.__signals = WeakSet()
        self.__type = kwargs.get("type", Signal.Auto)

        self.__emitting = False
        self.__connect_queue = []
        self.__disconnect_queue = []
    
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
    #   \param kargs The keyword arguments to pass along.
    #
    #   \note If the Signal type is Queued and this is not called from the application thread
    #   the call will be posted as an event to the application main thread, which means the
    #   function will be called on the next application event loop tick.
    def emit(self, *args, **kargs):
        try:
            if self.__type == Signal.Queued:
                Signal._app.functionEvent(CallFunctionEvent(self.emit, args, kargs))
                return

            if self.__type == Signal.Auto:
                if threading.current_thread() is not Signal._app.getMainThread():
                    Signal._app.functionEvent(CallFunctionEvent(self.emit, args, kargs))
                    return
        except AttributeError: # If Signal._app is not set
            return

        self.__emitting = True

        # Call handler functions
        for func in self.__functions:
            func(*args, **kargs)

        # Call handler methods
        for dest, funcs in self.__methods.items():
            for func in funcs:
                func(dest, *args, **kargs)

        # Emit connected signals
        for signal in self.__signals:
            signal.emit(*args, **kargs)

        self.__emitting = False
        for connector in self.__connect_queue:
            self.connect(connector)
        self.__connect_queue.clear()
        for connector in self.__disconnect_queue:
            self.disconnect(connector)
        self.__connect_queue.clear()

    ##  Connect to this signal.
    #   \param connector The signal or slot (function) to connect.
    def connect(self, connector):
        if self.__emitting:
            # When we try to connect to a signal we change the dictionary of connectors.
            # This will cause an Exception since we are iterating over a dictionary that changed.
            # So instead, defer the connections until after we are done emitting.
            self.__connect_queue.append(connector)
            return

        if type(connector) == Signal:
            if connector == self:
                return
            self.__signals.add(connector)
        elif inspect.ismethod(connector):
            if connector.__self__ not in self.__methods:
                self.__methods[connector.__self__] = set()

            self.__methods[connector.__self__].add(connector.__func__)
        else:
            self.__functions.add(connector)

    ##  Disconnect from this signal.
    #   \param connector The signal or slot (function) to disconnect.
    def disconnect(self, connector):
        if self.__emitting:
            # See above.
            self.__disconnect_queue.append(connector)
            return

        try:
            if connector in self.__signals:
                self.__signals.remove(connector)
            elif inspect.ismethod(connector) and connector.__self__ in self.__methods:
                self.__methods[connector.__self__].remove(connector.__func__)
            else:
                if connector in self.__functions:
                    self.__functions.remove(connector)

        except KeyError: #Ignore errors when connector is not connected to this signal.
            pass

    ##  Disconnect all connected slots.
    def disconnectAll(self):
        if self.__emitting:
            raise RuntimeError("Tried to disconnect signal while signal is being emitted")

        self.__functions.clear()
        self.__methods.clear()
        self.__signals.clear()

    ##  private:

    #   To avoid circular references when importing Application, this should be
    #   set by the Application instance.
    _app = None

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for name, signal in inspect.getmembers(self, lambda i: isinstance(i, Signal)):
            setattr(self, name, Signal(type = signal.getType()))
