# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject
import collections

##  Base class for plugins that extend the functionality of Uranium.
#   Every extension adds a (sub) menu to the extension menu with one or
#   more menu items.
class Extension(PluginObject):
    def __init__(self):
        super().__init__()
        self._menu_function_dict = collections.OrderedDict()
        self._menu_name = None

    ##  Add an item to the sub-menu of the extension
    #   \param name \type{string}
    #   \param function \type{function}
    def addMenuItem(self, name, function):
        self._menu_function_dict[name] = function

    ##  Set name of the menu where all menu items are placed in
    #   \param name \type{string}
    def setMenuName(self, name):
        self._menu_name = name

    ##  Get the name of the menu where all menu items are placed in
    #   \param menu name \type{string}
    def getMenuName(self):
        return self._menu_name

    ##  Call function associated with option
    #   \param name \type{string}
    def activateMenuItem(self, name):
        if name in self._menu_function_dict:
            self._menu_function_dict[name]()

    ##  Get list of all menu item names
    #   \return \type{list}
    def getMenuItemList(self):
        return list(self._menu_function_dict.keys())
