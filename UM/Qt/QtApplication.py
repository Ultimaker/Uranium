import sys
import os
import site
import signal
import platform

from PyQt5.QtCore import QObject, QCoreApplication, QEvent, pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication

from UM.Application import Application
from UM.Qt.QtGL2Renderer import QtGL2Renderer
from UM.Qt.Bindings.Bindings import Bindings
from UM.JobQueue import JobQueue

##  Application subclass that provides a Qt application object.
class QtApplication(QApplication, Application):
    def __init__(self):
        if platform.system() == "Windows":
            # QT needs to be able to find the Qt5 dlls on windows. However, these are installed in site-packages/PyQt5
            # Add this path to the environment so the dlls are found. (Normally the PyQt installer adds this path global.
            # However, we do not want to set system global paths from our applications)
            # This needs to be done before the QtApplication is initialized.
            for site_package_path in site.getsitepackages():
                pyqt_path = os.path.join(site_package_path, 'PyQt5')
                if os.path.isdir(pyqt_path):
                    os.environ['PATH'] = "%s;%s" % (pyqt_path, os.environ['PATH'])

        super().__init__(sys.argv)

        self._mainQml = "main.qml"
        self._engine = None
        self._renderer = None

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

    def getRenderer(self):
        if not self._renderer:
            self._renderer = QtGL2Renderer()

        return self._renderer

    #   Overridden from QApplication::setApplicationName to call our internal setApplicationName
    def setApplicationName(self, name):
        Application.setApplicationName(self, name)

    #   Handle a function that should be called later.
    def functionEvent(self, event):
        e = _QtFunctionEvent(event)
        QCoreApplication.postEvent(self, e)

    #   Handle Qt events
    def event(self, event):
        if event.type() == _QtFunctionEvent.QtFunctionEvent:
            event.functionEvent.call()
            return True

        return super().event(event)

##  Internal.
#
#   Wrapper around a FunctionEvent object to make Qt handle the event properly.
class _QtFunctionEvent(QEvent):
    QtFunctionEvent = QEvent.User + 1

    def __init__(self, fevent):
        super().__init__(self.QtFunctionEvent)
        self.functionEvent = fevent

