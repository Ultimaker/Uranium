# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import sys

from PyQt5.QtGui import QOpenGLVersionProfile, QOpenGLContext, QOpenGLFramebufferObject
from PyQt5.QtWidgets import QMessageBox

from UM.Logger import Logger

from UM.View.GL.OpenGL import OpenGL

from . import QtFrameBufferObject
from . import QtTexture
from . import QtShaderProgram

##  OpenGL subclass providing the PyQt OpenGL implementation.
class QtOpenGL(OpenGL):
    def __init__(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        if not self._gl:
            QMessageBox.critical("Failed to Initialize OpenGL", "Could not initialize OpenGL. Cura requires OpenGL 2.0 or higher. Please check your video card drivers.")
            sys.exit(1)

        if not self.hasFrameBufferObjects():
            QMessageBox.critical("Critical OpenGL Extensions Missing", "Critical OpenGL extensions are missing. Cura requires support for Framebuffer Objects. Please check your video card drivers.")
            sys.exit(1)

        self._gl.initializeOpenGLFunctions()

        self._gpu_vendor = OpenGL.Vendor.Other
        vendor_string = self._gl.glGetString(self._gl.GL_VENDOR).lower()
        if "nvidia" in vendor_string:
            self._gpu_vendor = OpenGL.Vendor.NVidia
        elif "amd" in vendor_string or "ati" in vendor_string:
            self._gpu_vendor = OpenGL.Vendor.AMD
        elif "intel" in vendor_string:
            self._gpu_vendor = OpenGL.Vendor.Intel

        self._gpu_type = self._gl.glGetString(self._gl.GL_RENDERER)

        if not self.hasFrameBufferObjects():
            Logger.log("w", "No frame buffer support, falling back to texture copies.")

        Logger.log("d", "Initialized OpenGL subsystems.")
        Logger.log("d", "OpenGL Version:  %s", self._gl.glGetString(self._gl.GL_VERSION))
        Logger.log("d", "OpenGL Vendor:   %s", self._gl.glGetString(self._gl.GL_VENDOR))
        Logger.log("d", "OpenGL Renderer: %s", self._gpu_type)

    def hasFrameBufferObjects(self):
        return QOpenGLFramebufferObject.hasOpenGLFramebufferObjects()

    def hasExtension(self, extension):
        return QOpenGLContext.currentContext().hasExtension(extension)

    def getGPUVendor(self):
        return self._gpu_vendor

    def getGPUType(self):
        return self._gpu_type

    def getBindingsObject(self):
        return self._gl

    def createFrameBufferObject(self, width, height):
        return QtFrameBufferObject.QtFrameBufferObject(width, height)

    def createTexture(self):
        return QtTexture.QtTexture()

    def createShaderProgram(self, file_name):
        shader = QtShaderProgram.QtShaderProgram()
        shader.load(file_name)
        return shader
