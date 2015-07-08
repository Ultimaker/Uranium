# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

##  Manages all available output devices and the factory objects used to create them.
#
#
class OutputDeviceManager(SignalEmitter):
    def __init__(self):
        super().__init__()

        self._output_devices = {}
        self._plugins = {}

        PluginRegistry.addType("output_device", self.addOutputDevicePlugin)

    def getOutputDevices(self):
        return self._output_devices.values()

    def getOutputDeviceNames(self):
        return self._output_devices.keys()

    def getOutputDevice(self, name):
        if not name in self._output_devices:
            return None

        return self._output_devices[name]

    outputDevicesChanged = Signal()

    def addOutputDevice(self, device):
        if device.getId() in self._output_devices:
            Logger.log("i", "Output Device %s already added", device.getId())
            return

        self._output_devices[device.getId()] = device
        self.outputDevicesChanged.emit()

    def removeOutputDevice(self, name):
        if name not in self._output_devices:
            return

        del self._output_devices[name]
        self.outputDevicesChanged.emit()

    def getDefaultOutputDevice(self):
        pass

    def addOutputDevicePlugin(self, plugin):
        if plugin.getPluginId() in self._plugins:
            Logger.log("i", "Output Device Plugin %s was already added", plugin.getPluginId())
            return

        self._plugins[plugin.getPluginId()] = plugin
        plugin.start()

    def removeOutputDevicePlugin(self, name):
        if name not in self._plugins:
            return

        self._plugins[name].stop()
        del self._plugins[name]
