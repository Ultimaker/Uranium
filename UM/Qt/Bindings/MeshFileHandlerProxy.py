from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Logger import Logger

class MeshFileHandlerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._mesh_handler = Application.getInstance().getMeshFileHandler()

    @pyqtProperty("QStringList", constant=True)
    def supportedReadFileTypes(self):
        fileTypes = []
        fileTypes.append("All Supported Files (*{0})(*{0})".format(' *'.join(self._mesh_handler.getSupportedFileTypesRead())))

        for ext in self._mesh_handler.getSupportedFileTypesRead():
            fileTypes.append("{0} file (*.{0})(*.{0})".format(ext[1:]))

        fileTypes.append("All Files (*.*)(*)")

        return fileTypes

    @pyqtProperty("QStringList", constant=True)
    def supportedWriteFileTypes(self):
        return self._mesh_handler.getSupportedFileTypesWrite()

def createMeshFileHandlerProxy(engine, scriptEngine):
    return MeshFileHandlerProxy()
