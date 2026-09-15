# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import pyqtSignal, QObject, pyqtProperty, pyqtSlot

from UM.PluginObject import PluginObject
from typing import Optional


class FileProvider(PluginObject, QObject):
    """Base class for plugins that aim to provide a file to Cura in an alternate fashion, other than using the local file
    explorer.

    Every new file provider adds an option to the Open File(s) menu.
    """

    enabledChanged = pyqtSignal()
    """Signal which informs whether the file provider has been enabled or disabled, so that it can be removed or added
    in the Open File(s) submenu"""

    def __init__(self) -> None:
        PluginObject.__init__(self)
        QObject.__init__(self)

        self._menu_item_display_text = None  # type: Optional[str]
        """
        Text that will be displayed as an option in the Open File(s) menu.
        """

        self._shortcut = None  # type: Optional[str]
        """
        Shortcut key combination (e.g. "Ctrl+O").
        """

        self._enabled = True
        """
        If the provider is not enabled, it should not be displayed in the interface.
        """

        self.priority = 0
        """
        Where it should be sorted in lists, or which should be tried first.
        """

    def setShortcut(self, shortcut: str):
        self._shortcut = shortcut

    @pyqtProperty(str, fset=setShortcut, constant=True)
    def shortcut(self) -> str:
        return self._shortcut

    def setMenuItemDisplayText(self, text: str):
        self._menu_item_display_text = text

    @pyqtProperty(str, fset=setMenuItemDisplayText, constant=True)
    def menuItemDisplayText(self) -> str:
        return self._menu_item_display_text

    @pyqtProperty(str, fset=setMenuItemDisplayText, constant=True)
    def menu_item_display_text(self) -> str:
        '''Duplicate of the menuItemDisplayText property, used for retro-compatibility purposes'''
        return self._menu_item_display_text

    def setEnabled(self, enabled: bool):
        if enabled != self._enabled:
            self._enabled = enabled
            self.enabledChanged.emit()

    @pyqtProperty(bool, fset=setEnabled, notify=enabledChanged)
    def enabled(self) -> bool:
        return self._enabled

    @pyqtSlot()
    def runSlot(self) -> None:
        '''
        Slot that calls the run() function. Technically we could directly declare the run() method to be a slot, but
        that requires doing so on all the overridden definitions of the methods in the plugins, so for
        retro-compatibility purposes, we just define this main slot.
        '''
        self.run()

    def run(self) -> None:
        """Call function associated with the file provider"""
        raise NotImplementedError
