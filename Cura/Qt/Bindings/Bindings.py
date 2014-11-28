from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType

from Cura.Qt.Bindings.MainWindow import MainWindow

from Cura.Qt.Bindings.ViewModel import ViewModel
from Cura.Qt.Bindings.ToolModel import ToolModel

from Cura.Qt.Bindings.ApplicationProxy import ApplicationProxy
from Cura.Qt.Bindings.ControllerProxy import ControllerProxy
from Cura.Qt.Bindings.BackendProxy import BackendProxy
from Cura.Qt.Bindings.SceneProxy import SceneProxy
from Cura.Qt.Bindings.Models import Models

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
