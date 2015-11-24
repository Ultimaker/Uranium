# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtGui import QOpenGLTexture, QImage

from UM.View.GL.Texture import Texture

class QtTexture(Texture):
    def __init__(self, width = 0, height = 0):
        super().__init__()

        self._qt_texture = QOpenGLTexture(QOpenGLTexture.Target2D)
        self._qt_texture.setSize(width, height)
        self._qt_texture.allocateStorage(QOpenGLTexture.RGBA, QOpenGLTexture.UInt32)

    def getTextureId(self):
        return self._qt_texture.textureId()

    def bind(self, unit):
        self._qt_texture.bind()

    def release(self):
        self._qt_texture.release()

    def getData(self):
        return None

    def setData(self, data):
        pass

