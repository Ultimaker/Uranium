# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType

from UM.Qt.Bindings import StageModel
from UM.Qt.Duration import Duration, DurationFormat

from . import MainWindow
from . import ViewModel
from . import ToolModel
from . import ApplicationProxy
from . import ControllerProxy
from . import BackendProxy
from . import ResourcesProxy
from . import OperationStackProxy
from UM.Mesh.MeshFileHandler import MeshFileHandler
from UM.Workspace.WorkspaceFileHandler import WorkspaceFileHandler
from . import PreferencesProxy
from . import Theme
from . import OpenGLContextProxy
from . import PointingRectangle
from . import ActiveToolProxy
from . import OutputDevicesModel
from . import SelectionProxy
from . import OutputDeviceManagerProxy
from . import i18nCatalogProxy
from . import ExtensionModel
from . import VisibleMessagesModel
from . import Utilities

from UM.Settings.Models.SettingDefinitionsModel import SettingDefinitionsModel
from UM.Settings.Models.DefinitionContainersModel import DefinitionContainersModel
from UM.Settings.Models.InstanceContainersModel import InstanceContainersModel
from UM.Settings.Models.ContainerStacksModel import ContainerStacksModel
from UM.Settings.Models.SettingPropertyProvider import SettingPropertyProvider
from UM.Settings.Models.SettingPreferenceVisibilityHandler import SettingPreferenceVisibilityHandler
from UM.Settings.Models.ContainerPropertyProvider import ContainerPropertyProvider


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
    def createResourcesProxy(cls, engine, script_engine):
        return ResourcesProxy.ResourcesProxy()

    @classmethod
    def createOperationStackProxy(cls, engine, script_engine):
        return OperationStackProxy.OperationStackProxy()

    @classmethod
    def createOpenGLContextProxy(cls, engine, script_engine):
        return OpenGLContextProxy.OpenGLContextProxy()

    @classmethod
    def register(self):
        qmlRegisterType(MainWindow.MainWindow, "UM", 1, 0, "MainWindow")
        qmlRegisterType(ViewModel.ViewModel, "UM", 1, 0, "ViewModel")
        qmlRegisterType(ToolModel.ToolModel, "UM", 1, 0, "ToolModel")
        qmlRegisterType(PointingRectangle.PointingRectangle, "UM", 1, 0, "PointingRectangle")
        qmlRegisterType(ExtensionModel.ExtensionModel, "UM", 1, 0, "ExtensionModel")
        qmlRegisterType(VisibleMessagesModel.VisibleMessagesModel, "UM", 1, 0, "VisibleMessagesModel")

        # Singleton proxy objects
        qmlRegisterSingletonType(ControllerProxy.ControllerProxy, "UM", 1, 0, "Controller", Bindings.createControllerProxy)
        qmlRegisterSingletonType(ApplicationProxy.ApplicationProxy, "UM", 1, 0, "Application", Bindings.createApplicationProxy)
        qmlRegisterSingletonType(BackendProxy.BackendProxy, "UM", 1, 0, "Backend", Bindings.createBackendProxy)
        qmlRegisterSingletonType(ResourcesProxy.ResourcesProxy, "UM", 1, 0, "Resources", Bindings.createResourcesProxy)
        qmlRegisterSingletonType(OperationStackProxy.OperationStackProxy, "UM", 1, 0, "OperationStack", Bindings.createOperationStackProxy)
        qmlRegisterSingletonType(MeshFileHandler, "UM", 1, 0, "MeshFileHandler", MeshFileHandler.getInstance)
        qmlRegisterSingletonType(PreferencesProxy.PreferencesProxy, "UM", 1, 0, "Preferences", PreferencesProxy.createPreferencesProxy)
        qmlRegisterSingletonType(Theme.Theme, "UM", 1, 0, "Theme", Theme.createTheme)
        qmlRegisterSingletonType(ActiveToolProxy.ActiveToolProxy, "UM", 1, 0, "ActiveTool", ActiveToolProxy.createActiveToolProxy)
        qmlRegisterSingletonType(SelectionProxy.SelectionProxy, "UM", 1, 0, "Selection", SelectionProxy.createSelectionProxy)

        qmlRegisterUncreatableType(Duration, "UM", 1, 0, "Duration", "")
        qmlRegisterUncreatableType(DurationFormat, "UM", 1, 0, "DurationFormat", "")

        # Additions after 15.06. Uses API version 1.1 so should be imported with "import UM 1.1"
        qmlRegisterType(OutputDevicesModel.OutputDevicesModel, "UM", 1, 1, "OutputDevicesModel")
        qmlRegisterType(i18nCatalogProxy.i18nCatalogProxy, "UM", 1, 1, "I18nCatalog")

        qmlRegisterSingletonType(OutputDeviceManagerProxy.OutputDeviceManagerProxy, "UM", 1, 1, "OutputDeviceManager", OutputDeviceManagerProxy.createOutputDeviceManagerProxy)

        # Additions after 2.1. Uses API version 1.2
        qmlRegisterType(SettingDefinitionsModel, "UM", 1, 2, "SettingDefinitionsModel")
        qmlRegisterType(DefinitionContainersModel, "UM", 1, 2, "DefinitionContainersModel")
        qmlRegisterType(InstanceContainersModel, "UM", 1, 2, "InstanceContainersModel")
        qmlRegisterType(ContainerStacksModel, "UM", 1, 2, "ContainerStacksModel")
        qmlRegisterType(SettingPropertyProvider, "UM", 1, 2, "SettingPropertyProvider")
        qmlRegisterType(SettingPreferenceVisibilityHandler, "UM", 1, 2, "SettingPreferenceVisibilityHandler")
        qmlRegisterType(ContainerPropertyProvider, "UM", 1, 2, "ContainerPropertyProvider")

        # Additions after 2.3;
        qmlRegisterSingletonType(WorkspaceFileHandler, "UM", 1, 3, "WorkspaceFileHandler", WorkspaceFileHandler.getInstance)
        qmlRegisterSingletonType(OpenGLContextProxy.OpenGLContextProxy, "UM", 1, 3, "OpenGLContextProxy", Bindings.createOpenGLContextProxy)

        # Additions after 3.1
        qmlRegisterType(StageModel.StageModel, "UM", 1, 4, "StageModel")

        # Additions after 4.6
        qmlRegisterSingletonType(Utilities.UrlUtil, "UM", 1, 5, "UrlUtil", Utilities.createUrlUtil)

    @staticmethod
    def addRegisterType(class_type: type, qml_import_name: str, major_version: int, minor_version: int, class_name: str) -> None:
        qmlRegisterType(class_type, qml_import_name, major_version, minor_version, class_name)
