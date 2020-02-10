# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.PluginObject import PluginObject
import collections
from typing import Optional, Any, Callable, List


class Extension(PluginObject):
    """Base class for plugins that extend the functionality of Uranium.

    Every extension adds a (sub) menu to the extension menu with one or
    more menu items.
    """

    def __init__(self):
        super().__init__()
        self._menu_function_dict = collections.OrderedDict()
        self._menu_name = None  # type: Optional[str]

    def addMenuItem(self, name: str, func: Callable[[], Any]):
        """Add an item to the sub-menu of the extension

        :param name: :type{string}
        :param function: :type{function}
        """

        self._menu_function_dict[name] = func

    def setMenuName(self, name: str):
        """Set name of the menu where all menu items are placed in

        :param name: :type{string}
        """

        self._menu_name = name

    def getMenuName(self) -> Optional[str]:
        """Get the name of the menu where all menu items are placed in"""

        return self._menu_name

    def activateMenuItem(self, name: str):
        """Call function associated with option

        :param name: :type{string}
        """

        if name in self._menu_function_dict:
            self._menu_function_dict[name]()

    def getMenuItemList(self) -> List[str]:
        """Get list of all menu item names

        :return: :type{list}
        """

        return list(self._menu_function_dict.keys())
