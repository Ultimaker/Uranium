from PyQt5.QtCore import Qt, QCoreApplication

from Cura.Qt.ListModel import ListModel

class SettingsModel(ListModel):
    NameRole = Qt.UserRole + 1
    CategoryRole =Qt.UserRole + 2
    def __init__(self, parent = None):
        super().__init__(parent)
        self._machine_settings = QCoreApplication.instance().getMachineSettings()
        self._updateSettings()
        
    def roleNames(self):
        return {self.NameRole:'name', self.CategoryRole:"category"}
        
    def _updateSettings(self):
        self.clear()
        settings = self._machine_settings.getAllSettings()
        for setting in settings:
            self.appendItem({"name":setting.getLabel(),"category":setting.getCategory().getLabel()})
        