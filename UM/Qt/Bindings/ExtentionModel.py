from PyQt5.QtCore import Qt

from UM.Application import Application

from UM.Qt.ListModel import ListModel

class ExtentionModel(ListModel):
    NameRole = Qt.UserRole + 1
    IconRole = Qt.UserRole + 2
    ToolActiveRole = Qt.UserRole + 3
    DescriptionRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)

        self._controller = Application.getInstance().getController()
       
        self.addRoleName(self.NameRole, 'name')
        self.addRoleName(self.IconRole, 'icon')
        self.addRoleName(self.ToolActiveRole, 'active')
        self.addRoleName(self.DescriptionRole, 'description')
        
        self._onExtentionChanged()
        
    def _onExtentionChanged(self):
        self.clear()
        self.appendItem({ 'name': "Calibrate", 'icon': 'default.png', 'active': False, 'description': "Calibrate" })
        self.appendItem({ 'name': "Scan", 'icon': 'scan.png', 'active': False, 'description': "IMA CHARGIN MA LAZOOOOOR" })