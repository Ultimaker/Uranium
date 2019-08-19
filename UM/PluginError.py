# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

##  \file PluginError.py
#   Error classes that are used by PluginRegistry or other plugins to signal errors.


##  A general class for any error raised by a plugin.
class PluginError(Exception):
    pass


##  Raised when a plugin could not be found.
class PluginNotFoundError(PluginError):
    def __str__(self):
        name = self.args[0]     # pylint: disable=unsubscriptable-object
        return "Could not find plugin " + name


##  Raised when a plugin provides incorrect metadata.
class InvalidMetaDataError(PluginError):
   def __str__(self):
        name = self.args[0]     # pylint: disable=unsubscriptable-object
        return "Invalid metadata for plugin " + name
