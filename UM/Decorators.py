# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import copy
import warnings

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
