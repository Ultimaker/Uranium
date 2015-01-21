from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Application import Application
from UM.Qt.ListModel import ListModel

class PluginsModel(ListModel):
    NameRole = Qt.UserRole + 1
    RequiredRole = Qt.UserRole + 2
    EnabledRole = Qt.UserRole + 3
    TypeRole = Qt.UserRole + 4
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._plugin_registery = QCoreApplication.instance().getPluginRegistry()
        self._required_plugins = QCoreApplication.instance().getRequiredPlugins()
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.RequiredRole, "required")
        self.addRoleName(self.EnabledRole, "enabled")
        self.addRoleName(self.TypeRole, "type")
        self._update()
    
    def _update(self):
        self.clear() 
        active_plugins = self._plugin_registery.getActivePlugins()
        for plugin in self._plugin_registery.getAllMetaData({}):
            self.appendItem({"name":plugin["name"],"required":plugin["name"] in self._required_plugins, "enabled":plugin["name"] in active_plugins,"type":plugin["type"]})
    
    @pyqtSlot(str,bool)
    def setEnabled(self, name, enabled):
        if enabled:
            self._plugin_registery.addActivePlugin(name)
        else:
            self._plugin_registery.removeActivePlugin(name)
        self._update()
    
    @pyqtSlot(str,result=str) 
    def getAboutText(self,name):
        for plugin in self._plugin_registery.getAllMetaData({}):
            if "about" in plugin and plugin["name"] == name:
                return plugin["about"]
        return "Nope"
    @pyqtSlot(str,result=str) 
    def getAuthorText(self,name):
        for plugin in self._plugin_registery.getAllMetaData({}):
            if "author" in plugin and plugin["name"] == name:
                return plugin["author"]
        return "John Doe"
    
    @pyqtSlot(str,result=str) 
    def getVersionText(self,name):
        for plugin in self._plugin_registery.getAllMetaData({}):
            if "version" in plugin and plugin["name"] == name:
                return plugin["version"]
        return "1.0"