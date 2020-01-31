# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal
from UM.View.GL.OpenGLContext import OpenGLContext


class OpenGLContextProxy(QObject):
    """Expose OpenGLContext functions to qml."""

    dummySignal = pyqtSignal(int, arguments = ["state"])

    @pyqtProperty(bool, notify = dummySignal)
    def isLegacyOpenGL(self):
        return OpenGLContext.isLegacyOpenGL()
