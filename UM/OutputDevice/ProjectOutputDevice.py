# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional

from PyQt5.QtCore import pyqtSignal, QObject

from UM.OutputDevice.OutputDevice import OutputDevice
from UM.i18n import i18nCatalog

catalog = i18nCatalog("uranium")


class ProjectOutputDevice(QObject, OutputDevice):
    """
    Extends the OutputDevice class for OutputeDevices that support saving project files.
    """

    enabledChanged = pyqtSignal()
    """Signal which informs whether the file provider has been enabled or disabled, so that it can be removed or added
    in the 'File->Save Project...' submenu"""

    def __init__(self, device_id: str, parent = None, **kwargs):
        super().__init__(device_id = device_id, parent = parent)

        self.enabled = True
        """
        Whether this device is enabled. Disabled devices are not displayed in the 'File->Save Project...' submenu
        """

        self.menu_entry_text = None  # type: Optional[str]
        """
        Text that appears as the title of the menu item in the 'File->Save Project...' submenu
        """

        self.shortcut = None  # type: Optional[str]
        """
        Shortcut key combination
        """
