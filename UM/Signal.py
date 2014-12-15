#   Author:  Thiago Marcos P. Santos
#   Author:  Christopher S. Case
#   Author:  David H. Bronke
#   Author:  Arjen Hiemstra
#   License: MIT

import inspect
from weakref import WeakSet, WeakKeyDictionary

##  Simple implementation of signals and slots.
#
#   Signals and slots can be used as a light weight event system. A class can
#   define signals that other classes can connect functions or methods to, called slots.
#   Whenever the signal is called, it will proceed to call the connected slots.
#
#   To create a signal, create an instance variable of type Signal. Other objects can then
#   use that variable's `connect()` method to connect methods, callables or signals to the
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
#   Based on http://code.activestate.com/recipes/577980-improved-signalsslots-implementation-in-python/
#
class Signal:
    def __init__(self):
        self.__functions = WeakSet()
        self.__methods = WeakKeyDictionary()
        self.__signals = WeakSet()

    def __call__(self):
        raise NotImplementedError("Call emit() to emit a signal")

    ##  Emit the signal, indirectly calling all connected slots.
    #   \param args The positional arguments to pass along.
    #   \param kargs The keyword arguments to pass along.
    def emit(self, *args, **kargs):
        #obj = inspect.currentframe().f_back.f_locals['self']

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

    ##  Connect to this signal.
    #   \param connector The signal or slot to connect.
    def connect(self, connector):
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
    #   \param connector The signal or slot to disconnect.
    def disconnect(self, connector):
        if connector in self.__signals:
            self.__signals.remove(connector)
        elif inspect.ismethod(connector) and connector.__self__ in self.__methods:
            self.__methods[connector.__self__].remove(connector.__func__)
        else:
            if connector in self.__functions:
                self.__functions.remove(connector)

    ##  Disconnect all connected slots.
    def disconnectAll(self):
        self.__functions.clear()
        self.__methods.clear()
        self.__signals.clear()

##  Convenience class to simplify signal creation.
#
#   This class is a Convenience class to simplify signal creation. Since signals
#   need to be instance variables, normally you would need to create all singals
#   in the class' `__init__` method. However, this makes them rather awkward to
#   document. This class instead makes it possible to declare them as class variables
#   and properly document them. During the call to `__init__()`, this class will
#   then search through all the properties of the instance and create instance
#   variables for each class variable that is an instance of Signal.
class SignalEmitter:
    ##  Initialize method.
    def __init__(self):
        for name in self.__dict__:
            if type(self.__dict__[name]) == Signal:
                setattr(self, name, Signal())
