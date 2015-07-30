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
        self._active_device = None
        self._active_device_override = False

        PluginRegistry.addType("output_device", self.addOutputDevicePlugin)

    writeStarted = Signal()
    writeProgress = Signal()
    writeFinished = Signal()
    writeError = Signal()
    writeSuccess = Signal()

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
        device.writeStarted.connect(self.writeStarted)
        device.writeProgress.connect(self.writeProgress)
        device.writeFinished.connect(self.writeFinished)
        device.writeError.connect(self.writeError)
        device.writeSuccess.connect(self.writeSuccess)
        self.outputDevicesChanged.emit()

    def removeOutputDevice(self, name):
        if name not in self._output_devices:
            return

        device = self._output_devices[name]
        del self._output_devices[name]
        device.writeStarted.disconnect(self.writeStarted)
        device.writeProgress.disconnect(self.writeProgress)
        device.writeFinished.disconnect(self.writeFinished)
        device.writeError.disconnect(self.writeError)
        device.writeSuccess.disconnect(self.writeSuccess)
        self.outputDevicesChanged.emit()

    def getDefaultOutputDevice(self):
        pass

    activeDeviceChanged = Signal()
    def getActiveDevice(self):
        return self._active_device
    def setActiveDevice(self, device_id):
        if not device_id in self._output_devices:
            return

        if not self._active_device or self._active_device.getId() != device_id:
            self._active_device = self.getOutputDevice(device_id)
            self._active_device_override = True
            self.activeDeviceChanged.emit()

    def resetActiveDevice(self):
        self._active_device = self._findHighestPriorityDevice()
        self._active_device_override = False
        self.activeDeviceChanged.emit()
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

    def getOutputDevicePlugin(self, name):
        if name not in self._plugins:
            return None

        return self._plugins[name]
    def _findHighestPriorityDevice(self):
        device = None
        for key, value in self._output_devices.items():
            if not device or value.getPriority() > device.getPriority():
                device = value

        return device
