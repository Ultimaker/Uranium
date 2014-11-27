import sys
import os.path
import signal

from PyQt5.QtCore import QObject
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication

from Cura.Application import Application
from Cura.Qt.Bindings.Bindings import Bindings

from Cura.Qt.Bindings.ViewModel import ViewModel

##  Application subclass that provides a Qt application object.
class QtApplication(QApplication, Application):
    def __init__(self):
        super(QtApplication, self).__init__(sys.argv)
        self._mainQml = "main.qml"
        self._engine = None

        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def run(self):
        pass

    def setMainQml(self, file):
        self._mainQml = file

    def initializeEngine(self):
        # TODO: Document native/qml import trickery
        Bindings.register()

        self._engine = QQmlApplicationEngine()
        self._engine.addImportPath(os.path.dirname(__file__) + "/qml")

        self.registerObjects(self._engine)

        self._engine.load(self._mainQml)

    def registerObjects(self, engine):
        pass
