##  Base class for plugins that extend the functionality of Uranium.
#   Every extension adds a (sub) menu to the extension menu with one or
#   more menu items. 
from UM.PluginObject import PluginObject
class Extension(PluginObject):
    def __init__(self):
        super().__init__()
        self._menu_function_dict = {}
        

    def addMenuItem(self, name, function):
        self._menu_function_dict[name] = function
    
    def activateMenuItem(self,name):
        if name in self._menu_function_dict:
            self._menu_function_dict[name]() 
                
    def getMenuItemList(self):
        return list(self._menu_function_dict.keys())