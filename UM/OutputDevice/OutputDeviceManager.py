# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from enum import Enum
from typing import Dict, Optional, TYPE_CHECKING

from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

if TYPE_CHECKING:
    from UM.OutputDevice.OutputDevice import OutputDevice
    from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin

# Used internally to determine plugins capable of 'manual' addition of devices, see also [add|remove]ManualDevice below.
class ManualDeviceAdditionAttempt(Enum):
    NO = 0,        # The plugin can't add a device 'manually' (or at least not with the given parameters).
    POSSIBLE = 1,  # The plugin will try to add the (specified) device 'manually', unless another plugin has priority.
    PRIORITY = 2   # The plugin has determined by the specified parameters that it's responsible for adding this device
                   #     and thus has priority. If this fails, the plugins that replied 'POSSIBLE' will be tried.
                   #     NOTE: This last value should be used with great care!

##  Manages all available output devices and the plugin objects used to create them.
#
#   This class is intended as the main entry point for anything relating to file saving.
#   For the most basic usage, call getActiveDevice() to get an output device, then
#   call OutputDevice::requestWrite() on the returned object.
#
#   Active Device
#   -------------
#
#   The active device by default is determined based on the priority of individual
#   OutputDevice instances when there is more than one OutputDevice available. When
#   adding a device, the active device will be updated with the highest priority device.
#   Should there be two devices with the same priority the active device will be the first
#   device encountered with that priority.
#
#   Calling setActiveDevice() will override this behaviour and instead force the active
#   device to the specified device. This active device will not change when a new device
#   is added or removed, but it will revert back to the default behaviour if the active
#   device is removed. Call resetActiveDevice() to reset the active device to the default
#   behaviour based on priority.
#
#   OutputDevicePlugin and OutputDevice creation/removal
#   ----------------------------------------------------
#
#   Each instance of an OutputDevicePlugin is meant as an OutputDevice creation object.
#   Subclasses of OutputDevicePlugin are meant to perform device lookup and listening
#   for events like device hot-plugging. When a new device has been detected, the plugin
#   class should create an instance of an OutputDevice subclass and add it to this
#   manager class using addOutputDevice(). Similarly, if a device has been removed the
#   OutputDevicePlugin is expected to call removeOutputDevice() to remove the proper
#   device.
#
@signalemitter
class OutputDeviceManager:
    def __init__(self) -> None:
        super().__init__()

        self._output_devices = {}  # type: Dict[str, OutputDevice]
        self._plugins = {}  # type: Dict[str, OutputDevicePlugin]
        self._active_device = None  # type: Optional[OutputDevice]
        self._active_device_override = False
        self._write_in_progress = False
        PluginRegistry.addType("output_device", self.addOutputDevicePlugin)

        self._is_running = False

    ##  Emitted whenever a registered device emits writeStarted.
    #
    #   \sa OutputDevice::writeStarted
    writeStarted = Signal()

    ##  Emitted whenever a registered device emits writeProgress.
    #
    #   \sa OutputDevice::writeProgress
    writeProgress = Signal()

    ##  Emitted whenever a registered device emits writeFinished.
    #
    #   \sa OutputDevice::writeFinished
    writeFinished = Signal()

    ##  Emitted whenever a registered device emits writeError.
    #
    #   \sa OutputDevice::writeError
    writeError = Signal()

    ##  Emitted whenever a registered device emits writeSuccess.
    #
    #   \sa OutputDevice::writeSuccess
    writeSuccess = Signal()

    ##  Emitted whenever a device has been added manually.
    manualDeviceAdded = Signal()

    ##  Emitted whenever a device has been removed manually.
    manualDeviceRemoved = Signal()

    ##  Get a list of all registered output devices.
    #
    #   \return \type{list} A list of all registered output devices.
    def getOutputDevices(self):
        return self._output_devices.values()

    ##  Get a list of all IDs of registered output devices.
    #
    #   \return \type{list} A list of all registered output device ids.
    def getOutputDeviceIds(self):
        return self._output_devices.keys()

    ##  Get an output device by ID.
    #
    #   \param device_id The ID of the device to retrieve.
    #   \return \type{OutputDevice} The output device corresponding to the ID or None if not found.
    def getOutputDevice(self, device_id: str) -> Optional["OutputDevice"]:
        return self._output_devices.get(device_id, None)

    ##  Emitted whenever an output device is added or removed.
    outputDevicesChanged = Signal()

    def start(self) -> None:
        for plugin_id, plugin in self._plugins.items():
            try:
                plugin.start()
            except Exception:
                Logger.logException("e", "Exception starting OutputDevicePlugin %s", plugin.getPluginId())

    def stop(self) -> None:
        for plugin_id, plugin in self._plugins.items():
            try:
                plugin.stop()
            except Exception:
                Logger.logException("e", "Exception starting OutputDevicePlugin %s", plugin.getPluginId())

    def startDiscovery(self) -> None:
        for plugin_id, plugin in self._plugins.items():
            try:
                plugin.startDiscovery()
            except Exception:
                Logger.logException("e", "Exception startDiscovery OutputDevicePlugin %s", plugin.getPluginId())

    def refreshConnections(self) -> None:
        for plugin_id, plugin in self._plugins.items():
            try:
                plugin.refreshConnections()
            except Exception:
                Logger.logException("e", "Exception refreshConnections OutputDevicePlugin %s", plugin.getPluginId())

    ##  Add and register an output device.
    #
    #   \param \type{OutputDevice} The output device to add.
    #
    #   \note Does nothing if a device with the same ID as the passed device was already added.
    def addOutputDevice(self, device: "OutputDevice") -> None:
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

        if not self._active_device or not self._active_device_override:
            self._active_device = self._findHighestPriorityDevice()
            self.activeDeviceChanged.emit()

    ##  Remove a registered device by ID
    #
    #   \param device_id The ID of the device to remove.
    #
    #   \note This does nothing if the device_id does not correspond to a registered device.
    #   \return Whether the device was successfully removed or not.
    def removeOutputDevice(self, device_id: str) -> bool:
        if device_id not in self._output_devices:
            Logger.log("w", "Could not find output device with id %s to remove", device_id)
            return False

        device = self._output_devices[device_id]
        del self._output_devices[device_id]
        device.writeStarted.disconnect(self.writeStarted)
        device.writeProgress.disconnect(self.writeProgress)
        device.writeFinished.disconnect(self.writeFinished)
        device.writeError.disconnect(self.writeError)
        device.writeSuccess.disconnect(self.writeSuccess)
        self.outputDevicesChanged.emit()

        if self._active_device is not None and self._active_device.getId() == device_id:
            self._write_in_progress = False
            self.resetActiveDevice()
        return True

    ##  Emitted whenever the active device changes.
    activeDeviceChanged = Signal()

    ##  Get the active device.
    def getActiveDevice(self):
        return self._active_device

    ##  Set the active device.
    #
    #   \param device_id The ID of the device to set as active device.
    #
    #   \note This does nothing if the device_id does not correspond to a registered device.
    #   \note This will override the default active device selection behaviour.
    def setActiveDevice(self, device_id: str) -> None:
        if device_id not in self._output_devices:
            return

        if not self._active_device or self._active_device.getId() != device_id:
            self._active_device = self.getOutputDevice(device_id)
            self._write_in_progress = False
            self._active_device_override = True
            self.activeDeviceChanged.emit()

    ##  Reset the active device to the default device.
    def resetActiveDevice(self) -> None:
        self._active_device = self._findHighestPriorityDevice()
        self._active_device_override = False
        self._write_in_progress = False
        self.activeDeviceChanged.emit()

    ##  Add an OutputDevicePlugin instance.
    #
    #   \param \type{OutputDevicePlugin} The plugin to add.
    #
    #   \note This does nothing if the plugin was already added.
    def addOutputDevicePlugin(self, plugin: "OutputDevicePlugin") -> None:
        if plugin.getPluginId() in self._plugins:
            Logger.log("i", "Output Device Plugin %s was already added.", plugin.getPluginId())
            return

        self._plugins[plugin.getPluginId()] = plugin
        if self._is_running:
            try:
                plugin.start()
            except Exception:
                Logger.logException("e", "Exception starting OutputDevicePlugin %s", plugin.getPluginId())

    ##  Remove an OutputDevicePlugin by ID.
    #
    #   \param plugin_id The ID of the plugin to remove.
    #
    #   \note This does nothing if the specified plugin_id was not found.
    def removeOutputDevicePlugin(self, plugin_id: str) -> None:
        Logger.log("d", "Remove output device plugin %s", plugin_id)
        if plugin_id not in self._plugins:
            return

        try:
            self._plugins[plugin_id].stop()
        except Exception as e:
            Logger.log("e", "Exception stopping plugin %s: %s", plugin_id, repr(e))

        del self._plugins[plugin_id]

    def getAllOutputDevicePlugins(self) -> Dict[str, "OutputDevicePlugin"]:
        return self._plugins

    ##  Get an OutputDevicePlugin by plugin ID
    #
    #   \param plugin_id The ID of the plugin to retrieve
    #
    #   \return The plugin corresponding to the specified ID or None if it was not found.
    def getOutputDevicePlugin(self, plugin_id: str) -> Optional["OutputDevicePlugin"]:
        return self._plugins.get(plugin_id, None)

    ##  private:

    def _findHighestPriorityDevice(self) -> Optional["OutputDevice"]:
        device = None
        for key, value in self._output_devices.items():
            if not device or value.getPriority() > device.getPriority():
                device = value

        return device
