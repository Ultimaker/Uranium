import inspect
from weakref import WeakSet, WeakKeyDictionary

##  Simple implementation of signals and slots.
#
#   Signals and slots can be used as a light weight event system. A class can
#   define signals that other classes can connect functions or methods to, called slots.
#   Whenever the signal is called, it will proceed to call the connected slots.
#
#   To create a signal, create an instance variable of type Signal, using "attribute = Signal()"
#   Other objects can then use `attribute.connect()` to connect slots to that signal.
#   To emit the signal, call emit on the signal like `attribute.emit()`. Arguments can be
#   passed along to the signal, but slots will need to handle them.
#
#   In addition, signals can be connected to other signals. This will emit the connected
#   signal whenever the signal is emitted.
#
#   Signal-slot connections are weak references and as such will not prevent objects
#   from being destroyed. In addition, all slots will be implicitly disconnected when
#   the signal is destroyed.
#
#   \warning It is imperative that the signals are created as instance variables, otherwise
#   emitting signals will get confused. In this codebase, we therefore declare signal class
#   variables with None to make them easy to document but set the actual signal objects in
#   the class' __init__() method.
#
#   Taken from http://code.activestate.com/recipes/577980-improved-signalsslots-implementation-in-python/
#
#   Author:  Thiago Marcos P. Santos
#   Author:  Christopher S. Case
#   Author:  David H. Bronke
#   Author:  Arjen Hiemstra
#   License: MIT
class Signal:
    def __init__(self):
        self._functions = WeakSet()
        self._methods = WeakKeyDictionary()
        self._signals = WeakSet()

    ## Emit the signal, indirectly calling all connected slots.
    def emit(self, *args, **kargs):
        # Call handler functions
        for func in self._functions:
            func(*args, **kargs)

        # Call handler methods
        for obj, funcs in self._methods.items():
            for func in funcs:
                func(obj, *args, **kargs)

        # Emit connected signals
        for signal in self._signals:
            signal.emit(*args, **kargs)

    ##  Connect to this signal.
    #   \param connector The signal or slot to connect.
    def connect(self, connector):
        if type(connector) == Signal:
            if connector == self:
                return
            self._signals.add(connector)
        elif inspect.ismethod(connector):
            if connector.__self__ not in self._methods:
                self._methods[connector.__self__] = set()

            self._methods[connector.__self__].add(connector.__func__)
        else:
            self._functions.add(connector)

    ##  Disconnect from this signal.
    #   \param connector The signal or slot to disconnect.
    def disconnect(self, connector):
        if type(connector) == Signal:
            if connector in self._signals:
                if connector == self:
                    return
                self._signals.remove(connector)
        if inspect.ismethod(connector):
            if connector.__self__ in self._methods:
                self._methods[connector.__self__].remove(connector.__func__)
        else:
            if connector in self._functions:
                self._functions.remove(connector)

    ##  Disconnect all connected slots.
    def disconnectAll(self):
        self._functions.clear()
        self._methods.clear()
        self._signals.clear()
