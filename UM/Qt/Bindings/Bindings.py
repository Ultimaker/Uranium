# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType

from UM.Qt.Duration import Duration, DurationFormat

from UM.Qt.Bindings.MainWindow import MainWindow

from UM.Qt.Bindings.ViewModel import ViewModel
from UM.Qt.Bindings.ToolModel import ToolModel

from UM.Qt.Bindings.ApplicationProxy import ApplicationProxy
from UM.Qt.Bindings.ControllerProxy import ControllerProxy
from UM.Qt.Bindings.BackendProxy import BackendProxy
from UM.Qt.Bindings.SceneProxy import SceneProxy
from UM.Qt.Bindings.Models import Models
from UM.Qt.Bindings.ResourcesProxy import ResourcesProxy

from . import OperationStackProxy
from . import JobsModel
from . import MeshFileHandlerProxy
from . import PreferencesProxy
from . import Theme
from . import AngledCornerRectangle
from . import PointingRectangle
from . import SettingCategoriesModel
from . import ActiveToolProxy
from . import ActiveViewProxy
from . import OutputDevicesModel
from . import SelectionProxy
from . import OutputDeviceManagerProxy
from . import MachineDefinitionsModel
from . import MachineInstancesModel
from . import ProfilesModel
from . import MachineManagerProxy
from . import MachineVariantsModel
from . import MachineMaterialsModel
from . import i18nCatalogProxy
from . import ActiveProfileProxy

class Bindings:
    @classmethod
    def createControllerProxy(self, engine, script_engine):
        return ControllerProxy()

    @classmethod
    def createApplicationProxy(self, engine, script_engine):
        return ApplicationProxy()

    @classmethod
    def createBackendProxy(self, engine, script_engine):
        return BackendProxy()

    @classmethod
    def createSceneProxy(self, engine, script_engine):
        return SceneProxy()

    @classmethod
    def createModels(self, engine, script_engine):
        return Models()

    @classmethod
    def createResourcesProxy(cls, engine, script_engine):
        return ResourcesProxy()

    @classmethod
    def createOperationStackProxy(cls, engine, script_engine):
        return OperationStackProxy.OperationStackProxy()

    @classmethod
    def register(self):
        qmlRegisterType(MainWindow, "UM", 1, 0, "MainWindow")
        qmlRegisterType(ViewModel, "UM", 1, 0, "ViewModel")
        #qmlRegisterType(FileModel, "UM", 1, 0, "FileModel")
        qmlRegisterType(ToolModel, "UM", 1, 0, "ToolModel")
        qmlRegisterType(JobsModel.JobsModel, "UM", 1, 0, "JobsModel")
        qmlRegisterType(SettingCategoriesModel.SettingCategoriesModel, "UM", 1, 0, "SettingCategoriesModel")
        qmlRegisterType(AngledCornerRectangle.AngledCornerRectangle, "UM", 1, 0, "AngledCornerRectangle")
        qmlRegisterType(PointingRectangle.PointingRectangle, "UM", 1, 0, "PointingRectangle")

        # Singleton proxy objects
        qmlRegisterSingletonType(ControllerProxy, "UM", 1, 0, "Controller", Bindings.createControllerProxy)
        qmlRegisterSingletonType(ApplicationProxy, "UM", 1, 0, "Application", Bindings.createApplicationProxy)
        qmlRegisterSingletonType(BackendProxy, "UM", 1, 0, "Backend", Bindings.createBackendProxy)
        qmlRegisterSingletonType(SceneProxy, "UM", 1, 0, "Scene", Bindings.createSceneProxy)
        qmlRegisterSingletonType(Models, "UM", 1, 0, "Models", Bindings.createModels)
        qmlRegisterSingletonType(ResourcesProxy, "UM", 1, 0, "Resources", Bindings.createResourcesProxy)
        qmlRegisterSingletonType(OperationStackProxy.OperationStackProxy, "UM", 1, 0, "OperationStack", Bindings.createOperationStackProxy)
        qmlRegisterSingletonType(MeshFileHandlerProxy.MeshFileHandlerProxy, "UM", 1, 0, "MeshFileHandler", MeshFileHandlerProxy.createMeshFileHandlerProxy)
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
        qmlRegisterType(MachineDefinitionsModel.MachineDefinitionsModel, "UM", 1, 1, "MachineDefinitionsModel")
        qmlRegisterType(MachineInstancesModel.MachineInstancesModel, "UM", 1, 1, "MachineInstancesModel")
        qmlRegisterType(MachineVariantsModel.MachineVariantsModel, "UM", 1, 1, "MachineVariantsModel")
        qmlRegisterType(MachineMaterialsModel.MachineMaterialsModel, "UM", 1, 1, "MachineMaterialsModel")
        qmlRegisterType(ProfilesModel.ProfilesModel, "UM", 1, 1, "ProfilesModel")

        qmlRegisterSingletonType(OutputDeviceManagerProxy.OutputDeviceManagerProxy, "UM", 1, 1, "OutputDeviceManager", OutputDeviceManagerProxy.createOutputDeviceManagerProxy)
        qmlRegisterSingletonType(MachineManagerProxy.MachineManagerProxy, "UM", 1, 1, "MachineManager", MachineManagerProxy.createMachineManagerProxy)
        qmlRegisterSingletonType(ActiveProfileProxy.ActiveProfileProxy, "UM", 1, 1, "ActiveProfile", ActiveProfileProxy.createActiveProfileProxy)
