# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty

from . import ViewModel
from . import ToolModel
from . import SettingsModel
from . import JobsModel
from . import MeshListModel
from . import PluginsModel
from . import ExtensionModel
from . import MachinesModel
from . import DirectoryListModel
from . import AvailableMachinesModel
from . import AddMachinesModel
from . import SettingCategoriesModel
from . import VisibleMessagesModel

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
        self._extension_model = None
        self._machines_model = None
        self._directory_list_model = None
        self._available_machines_model = None
        self._add_machines_model = None
        self._setting_categories_model = None
        self._visible_messages_model = None

    @pyqtProperty(ViewModel.ViewModel, constant = True)
    def viewModel(self):
        if not self._view_model:
            self._view_model = ViewModel.ViewModel()

        return self._view_model
    
    @pyqtProperty(VisibleMessagesModel.VisibleMessagesModel, constant = True)
    def visibleMessagesModel(self):
        if not self._visible_messages_model:
            self._visible_messages_model = VisibleMessagesModel.VisibleMessagesModel()

        return self._visible_messages_model
    
    @pyqtProperty(ToolModel.ToolModel, constant = True)
    def toolModel(self):
        if not self._tool_model:
            self._tool_model = ToolModel.ToolModel()

        return self._tool_model
    
    @pyqtProperty(ExtensionModel.ExtensionModel, constant = True)
    def extensionModel(self):
        if not self._extension_model:
            self._extension_model = ExtensionModel.ExtensionModel()

        return self._extension_model
    
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

    @pyqtProperty(AddMachinesModel.AddMachinesModel, constant = True)
    def addMachinesModel(self):
        if not self._add_machines_model:
            self._add_machines_model = AddMachinesModel.AddMachinesModel()
        return self._add_machines_model

    @pyqtProperty(DirectoryListModel.DirectoryListModel, constant = True)
    def directoryListModel(self):
        if not self._directory_list_model:
            self._directory_list_model = DirectoryListModel.DirectoryListModel()
        return self._directory_list_model

    @pyqtProperty(AvailableMachinesModel.AvailableMachinesModel, constant = True)
    def availableMachinesModel(self):
        if not self._available_machines_model:
            self._available_machines_model = AvailableMachinesModel.AvailableMachinesModel()
        return self._available_machines_model

    @pyqtProperty(SettingCategoriesModel.SettingCategoriesModel, constant = True)
    def settingCategoriesModel(self):
        if not self._setting_categories_model:
            self._setting_categories_model = SettingCategoriesModel.SettingCategoriesModel()
        return self._setting_categories_model
