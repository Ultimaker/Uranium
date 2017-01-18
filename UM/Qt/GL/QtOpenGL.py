# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import sys

from PyQt5.QtGui import QOpenGLVersionProfile, QOpenGLContext, QOpenGLFramebufferObject, QOpenGLBuffer
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
            Logger.log("e", "Startup failed due to OpenGL initialization failing")
            QMessageBox.critical(None, "Failed to Initialize OpenGL", "Could not initialize OpenGL. This program requires OpenGL 2.0 or higher. Please check your video card drivers.")
            sys.exit(1)

        # It would be nice to be able to not necessarily need OpenGL Framebuffer Object support, but
        # due to a limiation in PyQt, currently glReadPixels or similar methods are not available.
        # This means we can only get frame buffer contents through methods that indirectly call
        # those methods, in this case primarily QOpenGLFramebufferObject::toImage(), making us
        # hard-depend on Framebuffer Objects.
        if not self.hasFrameBufferObjects():
            Logger.log("e", "Starup failed, OpenGL does not support Frame Buffer Objects")
            QMessageBox.critical(None, "Critical OpenGL Extensions Missing", "Critical OpenGL extensions are missing. This program requires support for Framebuffer Objects. Please check your video card drivers.")
            sys.exit(1)

        self._gl.initializeOpenGLFunctions()

        self._gpu_vendor = OpenGL.Vendor.Other
        vendor_string = self._gl.glGetString(self._gl.GL_VENDOR)
        if vendor_string is None:
            vendor_string = "Unknown"
        vendor_string = vendor_string.lower()
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

    ##  Overrides OpenGL::hasFrameBufferObjects()
    def hasFrameBufferObjects(self):
        return QOpenGLFramebufferObject.hasOpenGLFramebufferObjects()

    ##  Overrides OpenGL::hasExtension()
    def hasExtension(self, extension):
        return QOpenGLContext.currentContext().hasExtension(extension)

    ##  Overrides OpenGL::getGPUVendor()
    def getGPUVendor(self):
        return self._gpu_vendor

    ##  Overrides OpenGL::getGPUType()
    def getGPUType(self):
        return self._gpu_type

    ##  Overrides OpenGL::getBindingsObject()
    def getBindingsObject(self):
        return self._gl

    ##  Overrides OpenGL::createFrameBufferObject()
    def createFrameBufferObject(self, width, height):
        return QtFrameBufferObject.QtFrameBufferObject(width, height)

    ##  Overrides OpenGL::createTexture()
    def createTexture(self):
        return QtTexture.QtTexture()

    ##  Overrides OpenGL::createShaderProgram()
    def createShaderProgram(self, file_name):
        shader = QtShaderProgram.QtShaderProgram()
        shader.load(file_name)
        return shader

    def createVertexBuffer(self, mesh, **kwargs):
        if not kwargs.get("force_recreate", False) and hasattr(mesh, OpenGL.VertexBufferProperty):
            return getattr(mesh, OpenGL.VertexBufferProperty)

        buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        buffer.create()
        buffer.bind()

        buffer_size = mesh.getVertexCount() * 3 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasNormals():
            buffer_size += mesh.getVertexCount() * 3 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasColors():
            buffer_size += mesh.getVertexCount() * 4 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasUVCoordinates():
            buffer_size += mesh.getVertexCount() * 2 * 4 # Vertex count * number of components * sizeof(float32)

        buffer.allocate(buffer_size)

        offset = 0
        vertices = mesh.getVerticesAsByteArray()
        if vertices is not None:
            buffer.write(0, vertices, len(vertices))
            offset += len(vertices)

        if mesh.hasNormals():
            normals = mesh.getNormalsAsByteArray()
            buffer.write(offset, normals, len(normals))
            offset += len(normals)

        if mesh.hasColors():
            colors = mesh.getColorsAsByteArray()
            buffer.write(offset, colors, len(colors))
            offset += len(colors)

        if mesh.hasUVCoordinates():
            uvs = mesh.getUVCoordinatesAsByteArray()
            buffer.write(offset, uvs, len(uvs))
            offset += len(uvs)

        buffer.release()

        setattr(mesh, OpenGL.VertexBufferProperty, buffer)
        return buffer

    def createIndexBuffer(self, mesh, **kwargs):
        if not mesh.hasIndices():
            return None

        if not kwargs.get("force_recreate", False) and hasattr(mesh, OpenGL.IndexBufferProperty):
            return getattr(mesh, OpenGL.IndexBufferProperty)

        buffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        buffer.create()
        buffer.bind()

        data = mesh.getIndicesAsByteArray()
        buffer.allocate(data, len(data))
        buffer.release()

        setattr(mesh, OpenGL.IndexBufferProperty, buffer)
        return buffer
