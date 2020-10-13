# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import inspect

from PyQt5.QtCore import pyqtProperty, pyqtSignal, QObject, QCoreApplication, pyqtSlot
from PyQt5.QtQml import QJSValue

from UM.i18n import i18nCatalog


class i18nCatalogProxy(QObject): # [CodeStyle: Ultimaker code style requires classes to start with a upper case. But i18n is lower case by convention.]
    def __init__(self, parent = None):
        super().__init__(parent)

        self._name = None
        self._catalog = None

        # Slightly hacky way of getting at the QML engine defined by QtApplication.
        engine = QCoreApplication.instance()._qml_engine

        self._i18n_function = self._wrapFunction(engine, self, self._call_i18n)
        self._i18nc_function = self._wrapFunction(engine, self, self._call_i18nc)
        self._i18np_function = self._wrapFunction(engine, self, self._call_i18np)
        self._i18ncp_function = self._wrapFunction(engine, self, self._call_i18ncp)

    def setName(self, name):
        if name != self._name:
            self._catalog = i18nCatalog(name)
            self.nameChanged.emit()

    nameChanged = pyqtSignal()

    @pyqtProperty(str, fset = setName, notify = nameChanged)
    def name(self):
        return self._name

    @pyqtProperty(QJSValue, notify = nameChanged)
    def i18n(self):
        return self._i18n_function

    @pyqtProperty(QJSValue, notify = nameChanged)
    def i18nc(self):
        return self._i18nc_function

    @pyqtProperty(QJSValue, notify = nameChanged)
    def i18np(self):
        return self._i18np_function

    @pyqtProperty(QJSValue, notify = nameChanged)
    def i18ncp(self):
        return self._i18ncp_function

    @pyqtSlot(str, result = str)
    def _call_i18n(self, message):
        return self._catalog.i18n(message)

    @pyqtSlot(str, str, result = str)
    def _call_i18nc(self, context, message):
        return self._catalog.i18nc(context, message)

    @pyqtSlot(str, str, int, result = str)
    def _call_i18np(self, single, multiple, counter):
        return self._catalog.i18np(single, multiple, counter)

    @pyqtSlot(str, str, str, int, result = str)
    def _call_i18ncp(self, context, single, multiple, counter):
        return self._catalog.i18ncp(context, single, multiple, counter)

    def _wrapFunction(self, engine, this_object, function):
        """Wrap a function in a bit of a javascript to re-trigger a method call on signal emit.

        This slightly magical method wraps a Python method exposed to QML in a JavaScript
        closure with the same signature as the Python method. This allows the closure to be
        exposed as a QML property instead of a QML slot. Using a property for this allows us
        to add a notify signal to re-trigger the method execution. Due to the way notify
        signals are handled by QML, re-triggering the method only needs a signal emit.

        :param engine: :type{QQmlEngine} The QML engine to use to evaluate JavaScript.
        :param this_object: :type{QObject} The object to call the function on.
        :param function: :type{Function} The function to call. Should be marked as pyqtSlot.

        :return: :type{QJSValue} A JavaScript closure that when called calls the wrapper Python method.

        :note Currently, only functions taking a fixed list of positional arguments are supported.

        :todo Move this to a more generic place so more things can use it.
        """

        # JavaScript code that wraps the Python method call in a closure
        wrap_js = """(function(this_object) {{
            return function({args}) {{ return this_object.{function}({args}) }}
        }})"""

        # Get the function name and argument list.
        function_name = function.__name__
        function_args = inspect.getfullargspec(function)[0]

        if function_args[0] == "self":
            function_args = function_args[1:] # Drop "self" from argument list

        # Replace arguments and function name with the proper values.
        wrapped_function = wrap_js.format(function = function_name, args = ", ".join(function_args))

        # Wrap the "this" object in a QML JSValue object.
        this_jsvalue = engine.newQObject(this_object)

        # Use the QML engine to evaluate the wrapped JS, then call that to retrieve the closure.
        result = engine.evaluate(wrapped_function).call([this_jsvalue])
        # Finally, return the resulting function.
        return result
