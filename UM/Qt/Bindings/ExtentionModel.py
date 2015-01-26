from PyQt5.QtCore import Qt, pyqtSlot,QCoreApplication

from UM.Application import Application

from UM.Qt.ListModel import ListModel

class ExtentionModel(ListModel):
    NameRole = Qt.UserRole + 1
    IconRole = Qt.UserRole + 2
    ToolActiveRole = Qt.UserRole + 3
    DescriptionRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)
        #QCoreApplication.instance().getPluginRegistry().
        self.addRoleName(self.NameRole, 'name')
        self.addRoleName(self.IconRole, 'icon')
        self.addRoleName(self.ToolActiveRole, 'active')
        self.addRoleName(self.DescriptionRole, 'description')
        
        self._onExtentionChanged()
    
    @pyqtSlot(str)
    def buttonClicked(self,name):
        if name == "Scan":
            #start scan
            pass
        elif name == "Calibrate":
            #start calibration
            pass
        
    
    def _onExtentionChanged(self):
        self.clear()
        