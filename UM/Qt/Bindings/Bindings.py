from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType

from UM.Qt.Bindings.MainWindow import MainWindow

from UM.Qt.Bindings.ViewModel import ViewModel
from UM.Qt.Bindings.ToolModel import ToolModel

from UM.Qt.Bindings.ApplicationProxy import ApplicationProxy
from UM.Qt.Bindings.ControllerProxy import ControllerProxy
from UM.Qt.Bindings.BackendProxy import BackendProxy
from UM.Qt.Bindings.SceneProxy import SceneProxy
from UM.Qt.Bindings.Models import Models
from UM.Qt.Bindings.ResourcesProxy import ResourcesProxy

class Bindings:
    @classmethod
    def createControllerProxy(self, engine, scriptEngine):
        return ControllerProxy()

    @classmethod
    def createApplicationProxy(self, engine, scriptEngine):
        return ApplicationProxy()

    @classmethod
    def createBackendProxy(self, engine, scriptEngine):
        return BackendProxy()

    @classmethod
    def createSceneProxy(self, engine, scriptEngine):
        return SceneProxy()

    @classmethod
    def createModels(self, engine, scriptEngine):
        return Models()

    @classmethod
    def createResourcesProxy(cls, engine, scriptEngine):
        return ResourcesProxy()

    @classmethod
    def register(self):
        qmlRegisterType(MainWindow, "Cura", 1, 0, "MainWindow")
        qmlRegisterType(ViewModel, "Cura", 1, 0, "ViewModel")
        #qmlRegisterType(FileModel, "Cura", 1, 0, "FileModel")
        qmlRegisterType(ToolModel, "Cura", 1, 0, "ToolModel")
        #qmlRegisterType(SettingModel

        # Singleton proxy objects
        qmlRegisterSingletonType(ControllerProxy, "Cura", 1, 0, "Controller", Bindings.createControllerProxy)
        qmlRegisterSingletonType(ApplicationProxy, "Cura", 1, 0, "Application", Bindings.createApplicationProxy)
        qmlRegisterSingletonType(BackendProxy, "Cura", 1, 0, "Backend", Bindings.createBackendProxy)
        qmlRegisterSingletonType(SceneProxy, "Cura", 1, 0, "Scene", Bindings.createSceneProxy)
        qmlRegisterSingletonType(Models, "Cura", 1, 0, "Models", Bindings.createModels)
        qmlRegisterSingletonType(ResourcesProxy, "Cura", 1, 0, "Resources", Bindings.createResourcesProxy)
