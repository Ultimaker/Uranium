# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import ast
import builtins  # To check against functions that are built-in in Python.
import math  # Imported here so it can be used easily by the setting functions.
import uuid  # Imported here so it can be used easily by the setting functions.
import base64  # Imported here so it can be used easily by the setting functions.
import hashlib  # Imported here so it can be used easily by the setting functions.
from types import CodeType
from typing import Any, Callable, Dict, FrozenSet, NamedTuple, Optional, Set, TYPE_CHECKING

from UM.Settings.Interfaces import ContainerInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext
from UM.Logger import Logger

if TYPE_CHECKING:
    from typing import FrozenSet


class IllegalMethodError(Exception):
    pass


def _debug_value(value: Any) -> Any:
    Logger.log("d", "Setting Function: %s", value)
    return value


#
# This class is used to evaluate Python codes (or you can call them formulas) for a setting's property. If a setting's
# property is a static type, e.g., a string, an int, a float, etc., its value will just be interpreted as it is, but
# when it's a Python code (formula), the value needs to be evaluated via this class.
#
class SettingFunction:
    ##  Constructor.
    #
    #   \param code The Python code this function should evaluate.
    def __init__(self, expression: str) -> None:
        super().__init__()

        self._code = expression

        #  Keys of all settings that are referenced to in this function.
        self._used_keys = frozenset()  # type: FrozenSet[str]
        self._used_values = frozenset()  # type: FrozenSet[str]

        self._compiled = None  # type: Optional[CodeType] #Actually an Optional['code'] object, but Python doesn't properly expose this 'code' object via any library.
        self._valid = False  # type: bool

        try:
            tree = ast.parse(self._code, "eval")

            result = _SettingExpressionVisitor().visit(tree)
            self._used_keys = frozenset(result.keys)
            self._used_values = frozenset(result.values)

            self._compiled = compile(self._code, repr(self), "eval")
            self._valid = True
        except (SyntaxError, TypeError) as e:
            Logger.log("e", "Parse error in function ({1}) for setting: {0}".format(str(e), self._code))
        except IllegalMethodError as e:
            Logger.log("e", "Use of illegal method {0} in function ({1}) for setting".format(str(e), self._code))
        except Exception as e:
            Logger.log("e", "Exception in function ({0}) for setting: {1}".format(str(e), self._code))

    ##  Call the actual function to calculate the value.
    #
    #   \param value_provider The container from which to get setting values in
    #   the formula.
    def __call__(self, value_provider: ContainerInterface, context: Optional[PropertyEvaluationContext] = None) -> Any:
        if not value_provider:
            return None

        if not self._valid:
            return None

        locals = {} # type: Dict[str, Any]
        # if there is a context, evaluate the values from the perspective of the original caller
        if context is not None:
            value_provider = context.rootStack()
        for name in self._used_values:
            value = value_provider.getProperty(name, "value", context)
            if value is None:
                continue

            locals[name] = value

        g = {}  # type: Dict[str, Any]
        g.update(globals())
        g.update(self.__operators)
        # override operators if there is any in the context
        if context is not None:
            g.update(context.context.get("override_operators", {}))

        try:
            if self._compiled:
                return eval(self._compiled, g, locals)
            Logger.log("e", "An error ocurred evaluating the function {0}.".format(self))
            return 0
        except Exception as e:
            Logger.logException("d", "An exception occurred in inherit function {0}: {1}".format(self, str(e)))
            return 0  # Settings may be used in calculations and they need a value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SettingFunction):
            return False

        return self._code == other._code

    ##  Returns whether the function is ready to be executed.
    #
    #   \return True if the function is valid, or False if it's not.
    def isValid(self) -> bool:
        return self._valid

    ##  Retrieve a set of the keys (strings) of all the settings used in this function.
    #
    #   \return A set of the keys (strings) of all the settings used in this functions.
    def getUsedSettingKeys(self) -> FrozenSet[str]:
        return self._used_keys

    def __str__(self) -> str:
        return "={0}".format(self._code)

    def __repr__(self) -> str:
        return "<UM.Settings.SettingFunction (0x{0:x}) ={1} >".format(id(self), self._code)

    ##  To support Pickle
    #
    #   Pickle does not support the compiled code, so instead remove it from the state.
    #   We can re-compile it later on anyway.
    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        del state["_compiled"]
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        self._compiled = compile(self._code, repr(self), "eval")

    ##  Expose a custom function to the code executed by SettingFunction
    #
    #   \param name What identifier to use in the executed code.
    #   \param operator A callable that implements the actual logic to execute.
    @classmethod
    def registerOperator(cls, name: str, operator: Callable) -> None:
        cls.__operators[name] = operator
        _SettingExpressionVisitor._knownNames.add(name)

    __operators = {
        "debug": _debug_value
    }


_VisitResult = NamedTuple("_VisitResult", [("values", Set[str]), ("keys", Set[str])])


# Helper class used to analyze a parsed function.
#
# It walks a Python AST generated from a Python expression. It will analyze the AST and
# produce two sets, one set of "used keys" and one set of "used values". "used keys" are
# setting keys (strings) that are used by the expression, whereas "used values" are
# actual variable references that are needed for the function to be executed.
class _SettingExpressionVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.values = set()  # type: Set[str]
        self.keys = set()  # type: Set[str]

    def visit(self, node: ast.AST) -> _VisitResult:
        super().visit(node)
        return _VisitResult(values = self.values, keys = self.keys)

    def visit_Name(self, node: ast.Name) -> None:  # [CodeStyle: ast.NodeVisitor requires this function name]
        if node.id in self._blacklist:
            raise IllegalMethodError(node.id)

        if node.id not in self._knownNames and node.id not in dir(builtins):
            self.values.add(node.id)
            self.keys.add(node.id)

    ##  This one is used before Python 3.8 to visit string types.
    #
    #   visit_Str will be marked as deprecated from Python 3.8 and onwards.
    def visit_Str(self, node: ast.AST) -> None:
        if node.s not in self._knownNames and node.s not in dir(builtins):  # type: ignore #AST uses getattr stuff, so ignore type of node.s.
            self.keys.add(node.s)  # type: ignore

    ##  This one is used on Python 3.8+ to visit string types.
    def visit_Constant(self, node: ast.AST) -> None:
        if isinstance(node.value, str) and node.value not in self._knownNames and node.value not in dir(builtins):  # type: ignore #AST uses getattr stuff, so ignore type of node.value.
            self.keys.add(node.value)  # type: ignore

    _knownNames = {
        "math",
        "max",
        "min",
        "debug",
        "sum",
        "len",
        "uuid",
        "hashlib",
        "base64"
    }  # type: Set[str]

    _blacklist = {
        "sys",
        "os",
        "import",
        "__import__",
        "eval",
        "exec",
        "subprocess",
    }  # type: Set[str]
