# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from UM.PluginObject import PluginObject


class VersionUpgrade(PluginObject):
    """A type of plug-in that upgrades the configuration from an old file format to a newer one.
    
    Each version upgrade plug-in can convert from some combinations of
    configuration types and versions to other types and versions. Which types
    and versions they can convert from though is completely free, and the
    conversion functions are referred to by the metadata of the plug-in. That's
    why this interface is basically empty. A plug-in object is needed for the
    plug-in registry.
    """

    def __init__(self):
        """Initialises a version upgrade plugin instance."""

        super().__init__()


class FormatException(Exception):
    """An exception to throw if the formatting of a file is wrong."""

    def __init__(self, message, file = ""):
        """Creates the exception instance.
        
        :param message: A message indicating what went wrong.
        :param file: The file it went wrong in.
        """

        self._message = message
        self._file = file

    def __str__(self):
        """Gives a human-readable representation of this exception.
        
        :return: A human-readable representation of this exception.
        """

        return "Exception parsing " + self._file + ": " + self._message


class InvalidVersionException(Exception):
    """An exception to throw if the version number of a file is wrong."""
    pass
