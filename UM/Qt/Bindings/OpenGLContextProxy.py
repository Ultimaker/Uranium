# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Qt.Factory.QtCore import QObject, pyqtProperty, pyqtSignal
from UM.View.GL.OpenGLContext import OpenGLContext


##  Expose OpenGLContext functions to qml.
class OpenGLContextProxy(QObject):
    dummySignal = pyqtSignal(int, arguments = ["state"])

    @pyqtProperty(bool, notify = dummySignal)
    def isLegacyOpenGL(self):
        return OpenGLContext.isLegacyOpenGL()
