# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import copy
import warnings
import inspect

from UM.Logger import Logger

##  Decorator that can be used to indicate a method has been deprecated
#
#   \param message The message to display when the method is called. Should include a suggestion about what to use.
#   \param since A version since when this method has been deprecated.
def deprecated(message, since = "Unknown"):
    def deprecated_decorator(function):
        def deprecated_function(*args, **kwargs):
            warning = "{0} is deprecated (since {1}): {2}".format(function, since, message)
            Logger.log("w", warning)
            warnings.warn(warning, DeprecationWarning, stacklevel=2)
            return function(*args, **kwargs)
        return deprecated_function
    return deprecated_decorator


##  Decorator to ensure the returned value is always a copy and never a direct reference
#
#   "Everything is a Reference" is not nice when dealing with value-types like a Vector or Matrix.
#   Since you hardly ever want to manipulate internal state of for example a SceneNode, most getters
#   should return a copy instead of the actual object. This decorator ensures that happens.
def ascopy(function):
    def copy_function(*args, **kwargs):
        return copy.deepcopy(function(*args, **kwargs))

    return copy_function

##  Decorator to conditionally call an extra function before calling the actual function.
#
#   This is primarily intended for conditional debugging.
def call_if_enabled(function, condition):
    if condition:
        def call_decorated(decorated_function):
            def call_function(*args, **kwargs):
                if hasattr(decorated_function, "__self__"):
                    function(decorated_function.__self__, *args, **kwargs)
                else:
                    function(*args, **kwargs)
                return decorated_function(*args, **kwargs)
            return call_function
        return call_decorated
    else:
        def call_direct(decorated_function):
            return decorated_function
        return call_direct

##  Class decorator that check to see if all methods of the base class have been reimplemented
#
#   This is meant as a simple sanity check. An interface here is defined as a class with
#   only functions. Any subclass is expected to reimplement all functions defined in the class,
#   excluding builtin functions like __getattr__.
def interface(cls):
    # First, sanity check the interface declaration to make sure it only contains methods
    non_functions = list(filter(lambda i: not i[0].startswith("__") and not inspect.isfunction(i[1]), inspect.getmembers(cls)))
    if non_functions:
        raise TypeError("Class {0} is declared as interface but includes non-method properties: {1}".format(cls, non_functions))

    # Then, replace the new method with a method that checks if all methods have been reimplemented
    old_new = cls.__new__
    def new_new(subclass, *args, **kwargs):
        for method in filter(lambda i: inspect.isfunction(i[1]) and not i[0].startswith("__"), inspect.getmembers(cls)):
            sub_method = getattr(subclass, method[0])
            if sub_method == method[1]:
                raise NotImplementedError("Class {0} does not implement the complete interface of {1}".format(subclass, cls))

            if inspect.signature(sub_method) != inspect.signature(method[1]):
                raise NotImplementedError("Method {0} of class {1} does not have the same signature as method {2} in interface {3}: {4} vs {5}".format(sub_method, subclass, method[1], cls, inspect.signature(sub_method), inspect.signature(method[1])))

        return old_new(subclass, *args, **kwargs)

    cls.__new__ = new_new
    return cls
