# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional, Callable

from UM.OutputDevice.OutputDeviceManager import ManualDeviceAdditionAttempt
from UM.PluginObject import PluginObject
from UM.Application import Application


class OutputDevicePlugin(PluginObject):
    """Base class for output device plugins.

    This class provides the base for any output device plugin that should be
    registered with the OutputDeviceManager. Each OutputDevicePlugin should
    implement device detection and add/remove devices as needed.

    For example, the Removable Device plugin searches for removable devices
    that have been plugged in and creates new OutputDevice objects for each.
    Additionally, whenever a removable device has been removed, it will remove
    the OutputDevice object from the OutputDeviceManager.

    :sa OutputDeviceManager
    """

    def __init__(self) -> None:
        super().__init__()

        self._output_device_manager = Application.getInstance().getOutputDeviceManager()

    def getOutputDeviceManager(self):
        """Convenience method to get the Application's OutputDeviceManager."""

        return self._output_device_manager

    def start(self) -> None:
        """Called by OutputDeviceManager to indicate the plugin should start its device detection."""

        raise NotImplementedError("Start should be implemented by subclasses")

    def stop(self) -> None:
        """Called by OutputDeviceManager to indicate the plugin should stop its device detection."""

        raise NotImplementedError("Stop should be implemented by subclasses")

    def canAddManualDevice(self, address: str = "") -> ManualDeviceAdditionAttempt:
        """Used to check if this adress makes sense to this plugin w.r.t. adding(/removing) a manual device.
        /return 'No', 'possible', or 'priority' (in the last case this plugin takes precedence, use with care).
        """

        return ManualDeviceAdditionAttempt.NO

    def addManualDevice(self, address: str, callback: Optional[Callable[[bool, str], None]] = None) -> None:
        """Add a manual device by the specified address (for example, an IP).
        The optional callback is a function with signature func(success: bool, address: str) -> None, where
        - success is a bool that indicates if the manual device's information was successfully retrieved.
        - address is the address of the manual device.
        """

        pass

    def removeManualDevice(self, key: str, address: Optional[str] = None) -> None:
        """Remove a manual device by either the name and/or the specified address.
        Since this may be asynchronous, use the 'removeDeviceSignal' when the machine actually has been added.
        """

        pass

    def startDiscovery(self) -> None:
        """Starts to discovery network devices that can be handled by this plugin."""

        pass

    def refreshConnections(self) -> None:
        """Refresh the available/discovered printers for an output device that handles network printers."""

        pass
