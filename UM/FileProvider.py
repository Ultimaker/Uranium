# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.PluginObject import PluginObject
from typing import Optional, Any, Callable


class FileProvider(PluginObject):
    """Base class for plugins that aim to provide a file to Cura in an alternate fashion.

    Every new file provider adds an option to the Open File(s) menu.

    FIXME review documentation
    """

    def __init__(self) -> None:
        super().__init__()
        self._menu_item_display_text = None  # type: Optional[str]
        self._menu_item_name = None  # type: Optional[str]
        self._function = None  # type: Optional[Callable]
        self._shortcut = None  # type: Optional[str]

    def setMenuItemDisplayText(self, display_text: str) -> None:
        """Set the text that will be displayed as an option in the file provider menu
        FIXME review documentation

        :param display_text: :type{string}
        """

        self._menu_item_display_text = display_text

    def getMenuItemDisplayText(self) -> Optional[str]:
        """Get the text that will be displayed as an option in the file provider menu
        FIXME review documentation"""

        return self._menu_item_display_text

    def setMenuItemName(self, name: str) -> None:
        """Set the name of the file provider
        FIXME review documentation"""

        self._menu_item_name = name

    def getMenuItemName(self) -> Optional[str]:
        """Get the name of the file provider
        FIXME review documentation"""

        return self._menu_item_name

    def setFunction(self, function: Callable[[], Any]) -> None:
        """Set function that starts the file provider
        FIXME review documentation
        """

        self._function = function

    def getFunction(self) -> Callable[[], Any]:
        """Get function that starts the file provider
        FIXME review documentation
        """

        return self._function

    def setShortcut(self, shortcut: str) -> None:
        """Set the shortcut that starts this file provider
        FIXME review documentation

        :param shortcut: :type{string}
        """

        self._shortcut = shortcut

    def getShortcut(self) -> Optional[str]:
        """Get the shortcut that starts this file provider
        FIXME review documentation"""

        return self._shortcut

    def activate(self) -> None:
        """Call function associated with the file provider
        FIXME review documentation
        """

        self._function()
