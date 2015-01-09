from PyQt5.QtCore import QObject, pyqtProperty

from . import ViewModel
from . import ToolModel
from . import SettingsModel
from . import JobsModel
from . import MeshListModel

##  This class is a workaround for a bug in PyQt.
#   For some reason, a QAbstractItemModel subclass instantiated from QML
#   will crash when it gets assigned to
class Models(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._viewModel = None
        self._toolModel = None
        self._settingsModel = None
        self._jobsModel = None
        self._meshListModel = None

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

    @pyqtProperty(JobsModel.JobsModel, constant = True)
    def jobsModel(self):
        if not self._jobsModel:
            self._jobsModel = JobsModel.JobsModel()
        return self._jobsModel
    
    @pyqtProperty(MeshListModel.MeshListModel, constant = True)
    def meshListModel(self):
        if not self._meshListModel:
            self._meshListModel = MeshListModel.MeshListModel()
        return self._meshListModel
