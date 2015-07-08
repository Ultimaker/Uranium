# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject
from UM.Application import Application

class OutputDevicePlugin(PluginObject):
    def __init__(self):
        super().__init__()

        self._output_device_manager = Application.getInstance().getOutputDeviceManager()

    def getOutputDeviceManager(self):
        return self._output_device_manager

    ##  Called by OutputDeviceManager to indicate the plugin should start listening for events.
    def start(self):
        raise NotImplementedError("Start should be implemented by subclasses")

    ##  Called by OutputDeviceManager to indicate the plugin should stop listening for events.
    def stop(self):
        raise NotImplementedError("Stop should be implemented by subclasses")
