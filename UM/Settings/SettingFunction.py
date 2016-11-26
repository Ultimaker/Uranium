# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import ast
import math # Imported here so it can be used easily by the setting functions.

from UM.Logger import Logger

class IllegalMethodError(Exception):
    pass

def _debug_value(value):
    Logger.log("d", "Setting Function: %s", value)
    return value

##  Encapsulates Python code that provides a simple value calculation function.
#
class SettingFunction:
    ##  Constructor.
    #
    #   \param code The Python code this function should evaluate.
    def __init__(self, code, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._code = code
        self._settings = set()  # Keys of all settings that are referenced to in this function.
        self._compiled = None
        self._valid = False

        try:
            tree = ast.parse(self._code, "eval")
            self._settings = frozenset(_SettingExpressionVisitor().visit(tree))
            self._compiled = compile(self._code, repr(self), "eval")
            self._valid = True
        except (SyntaxError, TypeError) as e:
            Logger.log("e", "Parse error in function ({1}) for setting: {0}".format(str(e), self._code))
        except IllegalMethodError as e:
            Logger.log("e", "Use of illegal method {0} in function ({1}) for setting".format(str(e), self._code))
        except Exception as e:
            Logger.log("e", "Exception in function ({0}) for setting: {1}".format(str(e), self._code))

    ##  Call the actual function to calculate the value.
    def __call__(self, value_provider, *args, **kwargs):
        if not value_provider:
            return None

        if not self._valid:
            return None

        locals = { }
        for name in self._settings:
            value = value_provider.getProperty(name, "value")
            if value is None:
                continue

            locals[name] = value

        g = {}
        g.update(globals())
        g.update(self.__operators)

        try:
            return eval(self._compiled, g, locals)
        except Exception as e:
            Logger.logException("d", "An exception occurred in inherit function %s", self)
            return 0  # Settings may be used in calculations and they need a value

    def __eq__(self, other):
        if not isinstance(other, SettingFunction):
            return False

        return self._code == other._code

    ##  Returns whether the function is ready to be executed.
    #
    #   \return True if the function is valid, or False if it's not.
    def isValid(self):
        return self._valid

    ##  Retrieve a set of the keys (strings) of all the settings used in this function.
    #
    #   \return A set of the keys (strings) of all the settings used in this functions.
    def getUsedSettingKeys(self):
        return self._settings

    def __str__(self):
        return "={0}".format(self._code)

    def __repr__(self):
        return "<UM.Settings.SettingFunction (0x{0:x}) ={1} >".format(id(self), self._code)

    ##  To support Pickle
    #
    #   Pickle does not support the compiled code, so instead remove it from the state.
    #   We can re-compile it later on anyway.
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_compiled"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._compiled = compile(self._code, repr(self), "eval")

    ##  Expose a custom function to the code executed by SettingFunction
    #
    #   \param name What identifier to use in the executed code.
    #   \param operator A callable that implements the actual logic to execute.
    @classmethod
    def registerOperator(cls, name, operator):
        cls.__operators[name] = operator
        _SettingExpressionVisitor._knownNames.append(name)

    __operators = {
        "debug": _debug_value
    }

# Helper class used to analyze a parsed function
class _SettingExpressionVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.names = []

    def visit(self, node):
        super().visit(node)
        return self.names

    def visit_Name(self, node): # [CodeStyle: ast.NodeVisitor requires this function name]
        if node.id in self._blacklist:
            raise IllegalMethodError(node.id)

        if node.id not in self._knownNames and node.id not in __builtins__:
            self.names.append(node.id)

    def visit_Str(self, node):
        if node.s not in self._knownNames and node.s not in __builtins__:
            self.names.append(node.s)

    _knownNames = [
        "math",
        "max",
        "min",
        "debug",
        "sum",
        "len"
    ]

    _blacklist = [
        "sys",
        "os",
        "import",
        "__import__",
        "eval",
        "exec",
        "subprocess",
    ]
