# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from PyQt5.QtCore import pyqtSignal

from UM.PluginObject import PluginObject
from typing import Optional


class FileProvider(PluginObject):
    """Base class for plugins that aim to provide a file to Cura in an alternate fashion, other than using the local file
    explorer.

    Every new file provider adds an option to the Open File(s) menu.
    """

    enabledChanged = pyqtSignal()
    """Signal which informs whether the file provider has been enabled or disabled, so that it can be removed or added
    in the Open File(s) submenu"""

    def __init__(self) -> None:
        super().__init__()
        self._menu_item_display_text = None  # type: Optional[str]
        self._menu_item_name = None  # type: Optional[str]
        self._shortcut = None  # type: Optional[str]
        self._enabled = True

    def setMenuItemDisplayText(self, display_text: str) -> None:
        """Set the text that will be displayed as an option in the Open File(s) menu.

        :param display_text: The text that represents the file provider in the Open File(s) menu.
        """

        self._menu_item_display_text = display_text

    def getMenuItemDisplayText(self) -> Optional[str]:
        """Get the text that represents the file provider in the Open File(s) menu."""

        return self._menu_item_display_text

    def setMenuItemName(self, name: str) -> None:
        """Set the name of the file provider."""

        self._menu_item_name = name

    def getMenuItemName(self) -> Optional[str]:
        """Get the name of the file provider"""

        return self._menu_item_name

    def setShortcut(self, shortcut: str) -> None:
        """Set the shortcut that triggers this file provider

        :param shortcut: The shortcut that triggers the file provider
        """

        self._shortcut = shortcut

    def getShortcut(self) -> Optional[str]:
        """Get the shortcut that triggers this file provider"""

        return self._shortcut

    def run(self) -> None:
        """Call function associated with the file provider"""
        raise NotImplementedError

    def setEnabled(self, enabled):
        """Sets the status of the file provider. If a file provider is disabled, it won't appear in the Open File(s)
        submenu."""

        self._enabled = enabled
        self.enabledChanged.emit()

    def isEnabled(self) -> bool:
        """Gets the enabled status of the file provider."""

        return self._enabled
