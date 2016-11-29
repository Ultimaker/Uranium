# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType

from UM.Qt.Duration import Duration, DurationFormat

from . import MainWindow
from . import ViewModel
from . import ToolModel
from . import ApplicationProxy
from . import ControllerProxy
from . import BackendProxy
from . import SceneProxy
from . import ResourcesProxy
from . import OperationStackProxy
from . import JobsModel
from UM.Mesh.MeshFileHandler import MeshFileHandler
from UM.Workspace.WorkspaceFileHandler import WorkspaceFileHandler
from . import PreferencesProxy
from . import Theme
from . import AngledCornerRectangle
from . import PointingRectangle
from . import ActiveToolProxy
from . import ActiveViewProxy
from . import OutputDevicesModel
from . import SelectionProxy
from . import OutputDeviceManagerProxy
from . import i18nCatalogProxy
from . import ExtensionModel
from . import PluginsModel
from . import VisibleMessagesModel

from . import MeshListModel

import UM.Settings.Models

class Bindings:
    @classmethod
    def createControllerProxy(self, engine, script_engine):
        return ControllerProxy.ControllerProxy()

    @classmethod
    def createApplicationProxy(self, engine, script_engine):
        return ApplicationProxy.ApplicationProxy()

    @classmethod
    def createBackendProxy(self, engine, script_engine):
        return BackendProxy.BackendProxy()

    @classmethod
    def createSceneProxy(self, engine, script_engine):
        return SceneProxy.SceneProxy()

    @classmethod
    def createResourcesProxy(cls, engine, script_engine):
        return ResourcesProxy.ResourcesProxy()

    @classmethod
    def createOperationStackProxy(cls, engine, script_engine):
        return OperationStackProxy.OperationStackProxy()

    @classmethod
    def register(self):
        qmlRegisterType(MainWindow.MainWindow, "UM", 1, 0, "MainWindow")
        qmlRegisterType(ViewModel.ViewModel, "UM", 1, 0, "ViewModel")
        qmlRegisterType(ToolModel.ToolModel, "UM", 1, 0, "ToolModel")
        qmlRegisterType(JobsModel.JobsModel, "UM", 1, 0, "JobsModel")
        qmlRegisterType(AngledCornerRectangle.AngledCornerRectangle, "UM", 1, 0, "AngledCornerRectangle")
        qmlRegisterType(PointingRectangle.PointingRectangle, "UM", 1, 0, "PointingRectangle")
        qmlRegisterType(ExtensionModel.ExtensionModel, "UM", 1, 0, "ExtensionModel")
        qmlRegisterType(PluginsModel.PluginsModel, "UM", 1, 0, "PluginsModel")
        qmlRegisterType(VisibleMessagesModel.VisibleMessagesModel, "UM", 1, 0, "VisibleMessagesModel")

        # Singleton proxy objects
        qmlRegisterSingletonType(ControllerProxy.ControllerProxy, "UM", 1, 0, "Controller", Bindings.createControllerProxy)
        qmlRegisterSingletonType(ApplicationProxy.ApplicationProxy, "UM", 1, 0, "Application", Bindings.createApplicationProxy)
        qmlRegisterSingletonType(BackendProxy.BackendProxy, "UM", 1, 0, "Backend", Bindings.createBackendProxy)
        qmlRegisterSingletonType(SceneProxy.SceneProxy, "UM", 1, 0, "Scene", Bindings.createSceneProxy)
        qmlRegisterSingletonType(ResourcesProxy.ResourcesProxy, "UM", 1, 0, "Resources", Bindings.createResourcesProxy)
        qmlRegisterSingletonType(OperationStackProxy.OperationStackProxy, "UM", 1, 0, "OperationStack", Bindings.createOperationStackProxy)
        qmlRegisterSingletonType(MeshFileHandler, "UM", 1, 0, "MeshFileHandler", MeshFileHandler.getInstance)
        qmlRegisterSingletonType(PreferencesProxy.PreferencesProxy, "UM", 1, 0, "Preferences", PreferencesProxy.createPreferencesProxy)
        qmlRegisterSingletonType(Theme.Theme, "UM", 1, 0, "Theme", Theme.createTheme)
        qmlRegisterSingletonType(ActiveToolProxy.ActiveToolProxy, "UM", 1, 0, "ActiveTool", ActiveToolProxy.createActiveToolProxy)
        qmlRegisterSingletonType(ActiveViewProxy.ActiveViewProxy, "UM", 1, 0, "ActiveView", ActiveViewProxy.createActiveViewProxy)
        qmlRegisterSingletonType(SelectionProxy.SelectionProxy, "UM", 1, 0, "Selection", SelectionProxy.createSelectionProxy)

        qmlRegisterUncreatableType(Duration, "UM", 1, 0, "Duration", "")
        qmlRegisterUncreatableType(DurationFormat, "UM", 1, 0, "DurationFormat", "")

        # Additions after 15.06. Uses API version 1.1 so should be imported with "import UM 1.1"
        qmlRegisterType(OutputDevicesModel.OutputDevicesModel, "UM", 1, 1, "OutputDevicesModel")
        qmlRegisterType(i18nCatalogProxy.i18nCatalogProxy, "UM", 1, 1, "I18nCatalog")

        qmlRegisterSingletonType(OutputDeviceManagerProxy.OutputDeviceManagerProxy, "UM", 1, 1, "OutputDeviceManager", OutputDeviceManagerProxy.createOutputDeviceManagerProxy)

        # Additions after 2.1. Uses API version 1.2
        qmlRegisterType(UM.Settings.Models.SettingDefinitionsModel, "UM", 1, 2, "SettingDefinitionsModel")
        qmlRegisterType(UM.Settings.Models.DefinitionContainersModel, "UM", 1, 2, "DefinitionContainersModel")
        qmlRegisterType(UM.Settings.Models.InstanceContainersModel, "UM", 1, 2, "InstanceContainersModel")
        qmlRegisterType(UM.Settings.Models.ContainerStacksModel, "UM", 1, 2, "ContainerStacksModel")
        qmlRegisterType(UM.Settings.Models.SettingPropertyProvider, "UM", 1, 2, "SettingPropertyProvider")
        qmlRegisterType(UM.Settings.Models.SettingPreferenceVisibilityHandler, "UM", 1, 2, "SettingPreferenceVisibilityHandler")
        qmlRegisterType(UM.Settings.Models.ContainerPropertyProvider, "UM", 1, 2, "ContainerPropertyProvider")
        qmlRegisterType(MeshListModel.MeshListModel, "UM", 1, 2, "MeshListModel")

        # Additions after 2.3;
        qmlRegisterSingletonType(WorkspaceFileHandler, "UM", 1, 3, "WorkspaceFileHandler", WorkspaceFileHandler.getInstance)
