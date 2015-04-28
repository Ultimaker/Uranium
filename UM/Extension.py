from UM.PluginObject import PluginObject


##  Base class for plugins that extend the functionality of Uranium.
#   Every extension adds a (sub) menu to the extension menu with one or
#   more menu items. 
class Extension(PluginObject):
    def __init__(self):
        super().__init__()
        self._menu_function_dict = {}
    
    ##  Add an item to the submenu of the extention
    #   \param name \type{string}
    #   \param function \type{function}
    def addMenuItem(self, name, function):
        self._menu_function_dict[name] = function
    
    ##  Call function associated with option 
    #   \param name \type{string}
    def activateMenuItem(self, name):
        if name in self._menu_function_dict:
            self._menu_function_dict[name]() 
    
    ##  Get list of all menu item names 
    #   \return \type{list}
    def getMenuItemList(self):
        return list(self._menu_function_dict.keys())