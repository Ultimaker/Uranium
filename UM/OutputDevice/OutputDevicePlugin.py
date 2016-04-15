# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject
from UM.Application import Application


##  Base class for output device plugins.
#
#   This class provides the base for any output device plugin that should be
#   registered with the OutputDeviceManager. Each OutputDevicePlugin should
#   implement device detection and add/remove devices as needed.
#
#   For example, the Removable Device plugin searches for removable devices
#   that have been plugged in and creates new OutputDevice objects for each.
#   Additionally, whenever a removable device has been removed, it will remove
#   the OutputDevice object from the OutputDeviceManager.
#
#   \sa OutputDeviceManager
class OutputDevicePlugin(PluginObject):
    def __init__(self):
        super().__init__()

        self._output_device_manager = Application.getInstance().getOutputDeviceManager()

    ##  Convenience method to get the Application's OutputDeviceManager.
    def getOutputDeviceManager(self):
        return self._output_device_manager

    ##  Called by OutputDeviceManager to indicate the plugin should start its device detection.
    def start(self):
        raise NotImplementedError("Start should be implemented by subclasses")

    ##  Called by OutputDeviceManager to indicate the plugin should stop its device detection.
    def stop(self):
        raise NotImplementedError("Stop should be implemented by subclasses")
