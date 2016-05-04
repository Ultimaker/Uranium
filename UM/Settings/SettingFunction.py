# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import ast

from UM.Logger import Logger

class IllegalMethodError(Exception):
    pass

##  Encapsulates Python code that provides a simple value calculation function.
#
class SettingFunction:
    ##  Constructor.
    #
    #   \param code The Python code this function should evaluate.
    def __init__(self, code, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._code = code
        self._settings = []
        self._compiled = None
        self._valid = False

        try:
            tree = ast.parse(self._code, "eval")
            self._settings = _SettingExpressionVisitor().visit(tree)
            self._compiled = compile(self._code, repr(self), "eval")
            self._valid = True
        except (SyntaxError, TypeError) as e:
            Logger.log("e", "Parse error in function ({1}) for setting: {0}".format(str(e), self._code))
        except IllegalMethodError as e:
            Logger.log("e", "Use of illegal method {0} in function ({2}) for setting".format(str(e), self._code))
        except Exception as e:
            Logger.log("e", "Exception in function ({1}) for setting: {1}".format(str(e), self._code))

    ##  Call the actual function to calculate the value.
    def __call__(self, value_provider, *args, **kwargs):
        if not value_provider:
            return None

        if not self._valid:
            return None

        locals = { }
        for name in self._settings:
            locals[name] = value_provider.getValue(name)

        return eval(self._compiled, globals(), locals)

    def __eq__(self, other):
        if not isinstance(other, SettingFunction):
            return False

        return self._code == other._code

    ##  Returns whether the function is ready to be executed.
    #
    #   \return True if the function is valid, or False if it's not.
    def isValid(self):
        return self._valid

    ##  Retrieve a list of the keys of all the settings used in this function.
    def getUsedSettings(self):
        return self._settings

    def __str__(self):
        return "SettingFunction({0})".format(self._code)

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

    _knownNames = [
        "math"
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
