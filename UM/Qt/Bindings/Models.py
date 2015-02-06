from PyQt5.QtCore import QObject, pyqtProperty

from . import ViewModel
from . import ToolModel
from . import SettingsModel
from . import JobsModel
from . import MeshListModel
from . import PluginsModel
from . import ExtentionModel
from . import MachinesModel
from . import DirectoryListModel

##  This class is a workaround for a bug in PyQt.
#   For some reason, a QAbstractItemModel subclass instantiated from QML
#   will crash when it gets assigned to
class Models(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._view_model = None
        self._tool_model = None
        self._settings_model = None
        self._jobs_model = None
        self._mesh_list_model = None
        self._plugins_model = None
        self._extention_model = None
        self._machines_model = None
        self._directory_list_model = None

    @pyqtProperty(ViewModel.ViewModel, constant = True)
    def viewModel(self):
        if not self._view_model:
            self._view_model = ViewModel.ViewModel()

        return self._view_model

    @pyqtProperty(ToolModel.ToolModel, constant = True)
    def toolModel(self):
        if not self._tool_model:
            self._tool_model = ToolModel.ToolModel()

        return self._tool_model
    
    @pyqtProperty(ExtentionModel.ExtentionModel, constant = True)
    def extentionModel(self):
        if not self._extention_model:
            self._extention_model = ExtentionModel.ExtentionModel()

        return self._extention_model
    
    @pyqtProperty(SettingsModel.SettingsModel, constant = True)
    def settingsModel(self):
        if not self._settings_model:
            self._settings_model = SettingsModel.SettingsModel()
        return self._settings_model

    @pyqtProperty(JobsModel.JobsModel, constant = True)
    def jobsModel(self):
        if not self._jobs_model:
            self._jobs_model = JobsModel.JobsModel()
        return self._jobs_model
    
    @pyqtProperty(MeshListModel.MeshListModel, constant = True)
    def meshListModel(self):
        if not self._mesh_list_model:
            self._mesh_list_model = MeshListModel.MeshListModel()
        return self._mesh_list_model
    
    @pyqtProperty(PluginsModel.PluginsModel, constant = True)
    def pluginsModel(self):
        if not self._plugins_model:
            self._plugins_model = PluginsModel.PluginsModel()
        return self._plugins_model

    @pyqtProperty(MachinesModel.MachinesModel, constant = True)
    def machinesModel(self):
        if not self._machines_model:
            self._machines_model = MachinesModel.MachinesModel()
        return self._machines_model

    @pyqtProperty(DirectoryListModel.DirectoryListModel, constant = True)
    def directoryListModel(self):
        if not self._directory_list_model:
            self._directory_list_model = DirectoryListModel.DirectoryListModel()
        return self._directory_list_model
