# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

##  \file PluginError.py
#   Error classes that are used by PluginRegistry or other plugins to signal errors.


##  A general class for any error raised by a plugin.
class PluginError(Exception):
    def __init__(self, error = None): #pylint: disable=bad-whitespace
        super().__init__()
        self._error = error

    def __str__(self):
        return self._error


##  Raised when a plugin could not be found.
class PluginNotFoundError(Exception):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def __str__(self):
        return "Could not find plugin " + self._name


##  Raised when a plugin provides incorrect metadata.
class InvalidMetaDataError(Exception):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def __str__(self):
        return "Invalid metadata for plugin " + self._name
