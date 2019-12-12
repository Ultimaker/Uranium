# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional, Callable

from UM.OutputDevice.OutputDeviceManager import ManualDeviceAdditionAttempt
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

    def __init__(self) -> None:
        super().__init__()

        self._output_device_manager = Application.getInstance().getOutputDeviceManager()

    ##  Convenience method to get the Application's OutputDeviceManager.
    def getOutputDeviceManager(self):
        return self._output_device_manager

    ##  Called by OutputDeviceManager to indicate the plugin should start its device detection.
    def start(self) -> None:
        raise NotImplementedError("Start should be implemented by subclasses")

    ##  Called by OutputDeviceManager to indicate the plugin should stop its device detection.
    def stop(self) -> None:
        raise NotImplementedError("Stop should be implemented by subclasses")

    ## Used to check if this adress makes sense to this plugin w.r.t. adding(/removing) a manual device.
    #  /return 'No', 'possible', or 'priority' (in the last case this plugin takes precedence, use with care).
    def canAddManualDevice(self, address: str = "") -> ManualDeviceAdditionAttempt:
        return ManualDeviceAdditionAttempt.NO

    ## Add a manual device by the specified address (for example, an IP).
    #  The optional callback is a function with signature func(success: bool, address: str) -> None, where
    #    - success is a bool that indicates if the manual device's information was successfully retrieved.
    #    - address is the address of the manual device.
    def addManualDevice(self, address: str, callback: Optional[Callable[[bool, str], None]] = None) -> None:
        pass

    ## Remove a manual device by either the name and/or the specified address.
    #  Since this may be asynchronous, use the 'removeDeviceSignal' when the machine actually has been added.
    def removeManualDevice(self, key: str, address: Optional[str] = None) -> None:
        pass

    ## Starts to discovery network devices that can be handled by this plugin.
    def startDiscovery(self) -> None:
        pass

    ## Refresh the available/discovered printers for an output device that handles network printers.
    def refreshConnections(self) -> None:
        pass
