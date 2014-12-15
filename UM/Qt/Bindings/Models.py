from PyQt5.QtCore import QObject, pyqtProperty

from . import ViewModel
from . import ToolModel
from . import SettingsModel

##  This class is a workaround for a bug in PyQt.
#   For some reason, a QAbstractItemModel subclass instantiated from QML
#   will crash when it gets assigned to
class Models(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._viewModel = None
        self._toolModel = None
        self._settingsModel = None

    @pyqtProperty(ViewModel.ViewModel, constant = True)
    def viewModel(self):
        if not self._viewModel:
            self._viewModel = ViewModel.ViewModel()

        return self._viewModel

    @pyqtProperty(ToolModel.ToolModel, constant = True)
    def toolModel(self):
        if not self._toolModel:
            self._toolModel = ToolModel.ToolModel()

        return self._toolModel
    
    @pyqtProperty(SettingsModel.SettingsModel, constant = True)
    def settingsModel(self):
        if not self._settingsModel:
            self._settingsModel = SettingsModel.SettingsModel()
        return self._settingsModel