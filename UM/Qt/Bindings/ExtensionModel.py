from PyQt5.QtCore import Qt, pyqtSlot,QCoreApplication

from UM.Application import Application
from UM.Qt.ListModel import ListModel

class ExtensionModel(ListModel):
    NameRole = Qt.UserRole + 1
    ActionsRole = Qt.UserRole + 2
    ExtensionRole = Qt.UserRole + 3
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.addRoleName(self.NameRole, 'name')
        self.addRoleName(self.ActionsRole, 'actions')
        self.addRoleName(self.ExtensionRole, 'extension')
        self._updateExtentionList()
        
        #print(self._items)
    
    def _updateExtentionList(self):
        #active_plugins = self._plugin_registery.getActivePlugins()
        for extension in Application.getInstance().getExtensions():
            meta_data =  Application.getInstance().getPluginRegistry().getMetaData(extension.getPluginId())
            
            if "plugin" in meta_data:
                self.appendItem({'name': meta_data["plugin"].get('name', None), 'actions':self.createActionsModel(extension.getMenuItemList()),'extension':extension})

    def createActionsModel(self, options):
        model = ListModel()
        model.addRoleName(self.NameRole,"text")
        for option in options:
            model.appendItem({"text": str(option)})
        return model    
    
    @pyqtSlot(str,str)
    def subMenuTriggered(self,extention_name, option_name):
        for item in self._items:
            if extention_name == item["name"]:
                item['extension'].activateMenuItem(option_name)