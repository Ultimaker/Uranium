from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from Cura.Qt.ListModel import ListModel

class SettingsModel(ListModel):
    NameRole = Qt.UserRole + 1
    CategoryRole =Qt.UserRole + 2
    VisibilityRole = Qt.UserRole + 3
    def __init__(self, parent = None):
        super().__init__(parent)
        self._machine_settings = QCoreApplication.instance().getMachineSettings()
        self._updateSettings()
        
    def roleNames(self):
        return {self.NameRole:'name', self.CategoryRole:"category", self.VisibilityRole:"visible"}
        
    def _updateSettings(self):
        self.clear()
        settings = self._machine_settings.getAllSettings()
        for setting in settings:
            self.appendItem({"name":setting.getLabel(),"category":setting.getCategory().getLabel(),"visible":False})
            
    @pyqtSlot(str)
    def toggleVisibilityByCategory(self, category_key):
        for index in range(0, len(self.items)):
            item = self.items[index]
            if item["category"] == category_key:
                self.setProperty(index, 'visible', not item['visible'])
            
        
        