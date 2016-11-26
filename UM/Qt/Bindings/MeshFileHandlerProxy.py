# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices

from UM.Application import Application
from UM.Logger import Logger
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.SceneNode import SceneNode
from UM.Scene.PointCloudNode import PointCloudNode
from UM.Mesh.MeshData import MeshType
from UM.Mesh.ReadMeshJob import ReadMeshJob
from UM.Mesh.WriteMeshJob import WriteMeshJob
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Message import Message

from UM.Decorators import deprecated

import os.path
import platform

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

class MeshFileHandlerProxy(QObject):
    @deprecated("MeshFileHandlerProxy is no longer required. Use MeshFileHandler directly", "2.4")
    def __init__(self, parent = None):
        super().__init__(parent)
        self._mesh_handler = Application.getInstance().getMeshFileHandler()
        self._scene = Application.getInstance().getController().getScene()

    @pyqtProperty("QStringList", constant=True)
    def supportedReadFileTypes(self):
        file_types = []
        all_types = []

        if platform.system() == "Linux":
            for ext, desc in self._mesh_handler.getSupportedFileTypesRead().items():
                file_types.append("{0} (*.{1} *.{2})".format(desc, ext.lower(), ext.upper()))
                all_types.append("*.{0} *.{1}".format(ext.lower(), ext.upper()))
        else:
            for ext, desc in self._mesh_handler.getSupportedFileTypesRead().items():
                file_types.append("{0} (*.{1})".format(desc, ext))
                all_types.append("*.{0}".format(ext))

        file_types.sort()
        file_types.insert(0, i18n_catalog.i18nc("@item:inlistbox", "All Supported Types ({0})", " ".join(all_types)))
        file_types.append(i18n_catalog.i18nc("@item:inlistbox", "All Files (*)"))

        return file_types

    @pyqtProperty("QStringList", constant=True)
    def supportedWriteFileTypes(self):
        file_types = []

        for item in self._mesh_handler.getSupportedFileTypesWrite():
            file_types.append("{0} (*.{1})".format(item["description"], item["extension"]))

        file_types.sort()

        return file_types

    @pyqtSlot(QUrl)
    def readLocalFile(self, file):
        if not file.isValid():
            return
        job = ReadMeshJob(file.toLocalFile())
        job.finished.connect(self._readMeshFinished)
        job.start()

    def _readMeshFinished(self, job):
        nodes = job.getResult()
        for node in nodes:
            node.setSelectable(True)
            node.setName(os.path.basename(job.getFileName()))

            op = AddSceneNodeOperation(node, self._scene.getRoot())
            op.push()
            self._scene.sceneChanged.emit(node)

def createMeshFileHandlerProxy(engine, script_engine):
    return MeshFileHandlerProxy()
