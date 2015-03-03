from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Logger import Logger

class MeshFileHandlerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._mesh_handler = Application.getInstance().getMeshFileHandler()

    @pyqtProperty("QStringList", constant=True)
    def supportedReadFileTypes(self):
        file_types = []
        all_types = []

        for ext, desc in self._mesh_handler.getSupportedFileTypesRead().items():
            file_types.append("{0} (*.{1})(*.{1})".format(desc, ext))
            all_types.append("*.{0}".format(ext))

        file_types.sort()
        file_types.insert(0, "All Supported Types ({0})({0})".format(" ".join(all_types)))
        file_types.append("All Files (*.*)(*)")

        return file_types

    @pyqtProperty("QStringList", constant=True)
    def supportedWriteFileTypes(self):
        #TODO: Implement
        return []

def createMeshFileHandlerProxy(engine, script_engine):
    return MeshFileHandlerProxy()
