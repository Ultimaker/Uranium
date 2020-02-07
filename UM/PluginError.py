# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


class PluginError(Exception):
    """Error classes that are used by PluginRegistry or other plugins to signal errors.

    A general class for any error raised by a plugin.
    """
    pass


class PluginNotFoundError(PluginError):
    """Raised when a plugin could not be found."""

    def __str__(self):
        name = super().__str__()
        return "Could not find plugin " + name


class InvalidMetaDataError(PluginError):
    """Raised when a plugin provides incorrect metadata."""

    def __str__(self):
        name = super().__str__()
        return "Invalid metadata for plugin " + name
