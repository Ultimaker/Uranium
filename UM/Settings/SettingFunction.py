# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import ast
# noinspection PyUnresolvedReferences
import base64  # Imported here so it can be used easily by the setting functions.
import builtins  # To check against functions that are built-in in Python.
# noinspection PyUnresolvedReferences
import hashlib  # Imported here so it can be used easily by the setting functions.
# noinspection PyUnresolvedReferences
import uuid  # Imported here so it can be used easily by the setting functions.
from types import CodeType
from typing import Any, Callable, Dict, FrozenSet, NamedTuple, Optional, Set, TYPE_CHECKING

# noinspection PyUnresolvedReferences
import math  # Imported here so it can be used easily by the setting functions.

from UM.Logger import Logger
from UM.Settings.Interfaces import ContainerInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext

if TYPE_CHECKING:
    from typing import FrozenSet


class IllegalMethodError(Exception):
    pass


def _debug_value(value: Any) -> Any:
    Logger.log("d", "Setting Function: %s", value)
    return value


class SettingFunction:
    """Evaluates Python formulas for a setting's property.

    If a setting's property is a static type, e.g. a string, an int, a float, etc., its value will just be interpreted
    as it is, but when it's a Python code (formula), the value needs to be evaluated via this class.
    """
    def __init__(self, expression: str) -> None:
        """Constructor.

        :param expression: The Python code this function should evaluate.
        """
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

    def __call__(self, value_provider: ContainerInterface, context: Optional[PropertyEvaluationContext] = None) -> Any:
        """Call the actual function to calculate the value.

        :param value_provider: The container from which to get setting values in the formula.
        :param context: The context in which the call needs to be executed
        """

        if not value_provider:
            return None

        if not self._valid:
            return None

        locals = {}  # type: Dict[str, Any]
        # If there is a context, evaluate the values from the perspective of the original caller
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
        # Override operators if there is any in the context
        if context is not None:
            g.update(context.context.get("override_operators", {}))

        try:
            if self._compiled:
                return eval(self._compiled, g, locals)
            Logger.log("e", "An error occurred evaluating the function {0}.".format(self))
            return 0
        except Exception as e:
            Logger.logException("d", "An exception occurred in inherit function {0}: {1}".format(self, str(e)))
            return 0  # Settings may be used in calculations and they need a value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SettingFunction):
            return False

        return self._code == other._code

    def __hash__(self) -> int:
        return hash(self._code)

    def isValid(self) -> bool:
        """Returns whether the function is ready to be executed.

        :return: True if the function is valid, or False if it's not.
        """

        return self._valid

    def getUsedSettingKeys(self) -> FrozenSet[str]:
        """Retrieve a set of the keys (strings) of all the settings used in this function.

        :return: A set of the keys (strings) of all the settings used in this functions.
        """

        return self._used_keys

    def __str__(self) -> str:
        return "={0}".format(self._code)

    def __repr__(self) -> str:
        return "<UM.Settings.SettingFunction (0x{0:x}) ={1} >".format(id(self), self._code)

    def __getstate__(self) -> Dict[str, Any]:
        """To support Pickle

        Pickle does not support the compiled code, so instead remove it from the state.
        We can re-compile it later on anyway.
        """

        state = self.__dict__.copy()
        del state["_compiled"]
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        self._compiled = compile(self._code, repr(self), "eval")

    @classmethod
    def registerOperator(cls, name: str, operator: Callable) -> None:
        """Expose a custom function to the code executed by SettingFunction

        :param name: What identifier to use in the executed code.
        :param operator: A callable that implements the actual logic to execute.
        """

        cls.__operators[name] = operator
        _SettingExpressionVisitor._knownNames.add(name)

    __operators = {
        "debug": _debug_value
    }


_VisitResult = NamedTuple("_VisitResult", [("values", Set[str]), ("keys", Set[str])])


class _SettingExpressionVisitor(ast.NodeVisitor):
    """
    Helper class used to analyze a parsed function.

    It walks a Python AST generated from a Python expression. It will analyze the AST and produce two sets, one set of
    "used keys" and one set of "used values". "used keys" are setting keys (strings) that are used by the expression,
    whereas "used values" are actual variable references that are needed for the function to be executed.
    """
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

    def visit_DictComp(self, node: ast.DictComp) -> None:
        # This is mostly because there is no reason to use it at the moment. It might also be an attack vector.
        raise IllegalMethodError("Dict Comprehension is not allowed")

    def visit_ListComp(self, node):
        # This is mostly because there is no reason to use it at the moment. It might also be an attack vector.
        raise IllegalMethodError("List Comprehension is not allowed")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr not in self._knownNames:
            raise IllegalMethodError(node.attr)
        self.visit(node.value)  # Go a step deeper

    def generic_visit(self, node):
        for child_node in ast.iter_child_nodes(node):
            self.visit(child_node)

    def visit_Slice(self, node):
        """
        Visitor function for slices.
        We want to block all usage of slices, since it can be used to wiggle your way around the string filtering.
        For example: "_0"[:1] + "_0"[:1] + "import__" will still result in the final string "__import__"
        :param node:
        :return:
        """
        raise IllegalMethodError("Slices are not allowed")

    def visit_Str(self, node: ast.Str) -> None:
        """This one is used before Python 3.8 to visit string types.

        visit_Str will be marked as deprecated from Python 3.8 and onwards.
        """
        # The blacklisting is done just in case (All function calls should be whitelisted. The blacklist is to make
        # extra sure that certain calls are *not* made!)
        if node.s in self._blacklist:
            raise IllegalMethodError(node.s)
        if node.s.startswith("_"):
            raise IllegalMethodError(node.s)

        if node.s not in self._knownNames and node.s not in dir(builtins):  # type: ignore #AST uses getattr stuff, so ignore type of node.s.
            self.keys.add(node.s)  # type: ignore

    def visit_Subscript(self, node: ast.Index):
        if type(node.value) == ast.Str:
            raise IllegalMethodError("Indexing on strings is not allowed")
        if type(node.value) == getattr(ast, "Constant", None) and isinstance(getattr(node.value, "value", None), str):
            raise IllegalMethodError("Indexing on strings is not allowed")
        for child_node in ast.iter_child_nodes(node):
            self.visit(child_node)

    def visit_Constant(self, node) -> None:
        """This one is used on Python 3.8+ to visit constant string, bool, int and float types."""
        # The blacklisting is done just in case (All function calls should be whitelisted. The blacklist is to make
        # extra sure that certain calls are *not* made!)
        if not isinstance(node.value, str):
            # bool, int and float constants are allowed
            return

        if node.value in self._blacklist:
            raise IllegalMethodError(node.value)
        if node.s.startswith("_"):
            raise IllegalMethodError(node.s)
        if node.value not in self._knownNames and node.value not in dir(builtins):  # type: ignore #AST uses getattr stuff, so ignore type of node.value.
            self.keys.add(node.value)  # type: ignore

    _knownNames = {
        "math",
        "round",
        "max",
        "ceil",
        "min",
        "sqrt",
        "log",
        "tan",
        "cos",
        "sin",
        "atan",
        "acos",
        "asin",
        "pi",
        "floor",
        "debug",
        "sum",
        "len",
        "uuid",
        "hashlib",
        "base64",
        "uuid3",
        "NAMESPACE_DNS",
        "decode",
        "encode",
        "b64encode",
        "digest",
        "md5",
        "radians",
        "degrees",
        "lower",
        "upper",
        "startswith",
        "endswith",
        "capitalize"
    }  # type: Set[str]

    _blacklist = {
        "sys",
        "os",
        "delattr",
        "getattr",
        "dir",
        "open",
        "write",
        "compile",
        "import",
        "__import__",
        "__self__",
        "_",  # Because you can use this guy to create a number of the other blacklisted strings
        "__",
        ".",
        "_._",   # Just in case (I also don't see a reason for someone to use a string named like that...)
        "__enter__",
        "__builtins__",
        "eval",
        "exec",
        "execfile",
        "file",
        "subprocess",
        "globals",
        "__class__"
        "__globals__"
        "hasattr",
        "raw_input",
        "input",
        "reload",
        "setattr",
        "vars",
        "locals",
        "system",
        "literal_eval",
        "ast.literal_eval",
        "ast",
        "lambda",
        "__getattribute__",
        "__setattr__",
        "find_module",
        "__pycache__",
        "__file__"
    }  # type: Set[str]

    _allowed_builtins = {
        "bool",
        "True",
        "False",
        "None",
        "float",
        "int",
        "str",
        "sum",
        "pow",
        "abs",
        "all",
        "any",
        "round",
        "divmod",
        "hash",
        "len",
        "max",
        "min",
        "map"
    }  # type: Set[str]

    _disallowed_builtins = set(dir(builtins)) - _allowed_builtins
    _blacklist |= _disallowed_builtins
