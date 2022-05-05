# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional

from PyQt6.QtCore import pyqtSignal, QObject

from UM.Application import Application
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.Signal import signalemitter
from UM.i18n import i18nCatalog

catalog = i18nCatalog("uranium")


@signalemitter
class ProjectOutputDevice(QObject, OutputDevice):
    """
    Extends the OutputDevice class for OutputeDevices that support saving project files.
    """

    enabledChanged = pyqtSignal()
    """Signal which informs whether the project output device has been enabled or disabled, so that it can be added or removed 
     from the 'File->Save Project...' submenu"""

    last_out_name = None  # type: Optional[str]
    """Last output project name, gives the possibility to do something with the updated project-name on saving, if any.
    """

    def __init__(self, device_id: str, add_to_output_devices: bool = False, parent = None, **kwargs):
        super().__init__(device_id = device_id, parent = parent)

        self._enabled = True
        """
        Whether this device is enabled. Disabled devices are not displayed in the 'File->Save Project...' submenu nor in
        the OutputDevicesActionButton.
        """

        self.add_to_output_devices = add_to_output_devices
        """
        Boolean to determine whether the device should also be added to the _output_devices list. If that happens, the 
        device will appear as an option also in the OutputDevicesActionButton.
        """

        self.menu_entry_text = None  # type: Optional[str]
        """
        Text that appears as the title of the menu item in the 'File->Save Project...' submenu
        """

        self.shortcut = None  # type: Optional[str]
        """
        Shortcut key combination
        """

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Setter for the enable property. It ensures that a project output device that gets enabled is also added to
        the output devices, if that is necessary.

        :param enabled: Whether the device should be enabled or disabled
        """
        if enabled != self._enabled:
            self._enabled = enabled
            self.enabledChanged.emit()

            if self.add_to_output_devices:
                # When a project output device is intended to be added to the output devices, we need to make sure that
                # whenever it gets enabled it is added, and when it gets disabled it is removed from the output devices
                if self._enabled:
                    Application.getInstance().getOutputDeviceManager().addOutputDevice(self)
                else:
                    Application.getInstance().getOutputDeviceManager().removeOutputDevice(self.getId())

    @staticmethod
    def getLastOutputName() -> Optional[str]:
        return ProjectOutputDevice.last_out_name

    @staticmethod
    def setLastOutputName(name: Optional[str] = None) -> None:
        ProjectOutputDevice.last_out_name = name
