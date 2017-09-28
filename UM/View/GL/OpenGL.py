# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import sys
import ctypes   # type: ignore

from PyQt5.QtGui import QOpenGLVersionProfile, QOpenGLContext, QOpenGLFramebufferObject, QOpenGLBuffer, QSurfaceFormat
from PyQt5.QtWidgets import QMessageBox

from UM.Logger import Logger

from UM.View.GL import FrameBufferObject
from UM.View.GL import ShaderProgram
from UM.View.GL.ShaderProgram import InvalidShaderProgramError
from UM.View.GL import Texture
from UM.View.GL.OpenGLContext import OpenGLContext
from UM.i18n import i18nCatalog #To make dialogs translateable.
i18n_catalog = i18nCatalog("uranium")

##  Convenience methods for dealing with OpenGL.
#
#   This class simplifies dealing with OpenGL and different Python OpenGL bindings. It
#   mostly describes an interface that should be implemented for dealing with basic OpenGL
#   functionality using these different OpenGL bindings. Additionally, it provides singleton
#   handling. The implementation-defined subclass must be set as singleton instance as soon
#   as possible so that any calls to getInstance() return a proper object.
class OpenGL(object):
    VertexBufferProperty = "__vertex_buffer"
    IndexBufferProperty = "__index_buffer"

    ##  Different OpenGL chipset vendors.
    class Vendor:
        NVidia = 1
        AMD = 2
        Intel = 3
        Other = 4

    def __init__(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(OpenGLContext.major_version, OpenGLContext.minor_version)
        profile.setProfile(OpenGLContext.profile)

        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        if not self._gl:
            Logger.log("e", "Startup failed due to OpenGL initialization failing")
            QMessageBox.critical(None, i18n_catalog.i18nc("@message", "Failed to Initialize OpenGL", "Could not initialize OpenGL. This program requires OpenGL 2.0 or higher. Please check your video card drivers."))
            sys.exit(1)

        # It would be nice to be able to not necessarily need OpenGL Framebuffer Object support, but
        # due to a limiation in PyQt, currently glReadPixels or similar methods are not available.
        # This means we can only get frame buffer contents through methods that indirectly call
        # those methods, in this case primarily QOpenGLFramebufferObject::toImage(), making us
        # hard-depend on Framebuffer Objects.
        if not self.hasFrameBufferObjects():
            Logger.log("e", "Starup failed, OpenGL does not support Frame Buffer Objects")
            QMessageBox.critical(None, i18n_catalog.i18nc("Critical OpenGL Extensions Missing", "Critical OpenGL extensions are missing. This program requires support for Framebuffer Objects. Please check your video card drivers."))
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

        #WORKAROUND: Cura/#1117 Cura-packaging/12
        # Some Intel GPU chipsets return a string, which is not undecodable via PyQt5.
        # This workaround makes the code fall back to a "Unknown" renderer in these cases.
        try:
            self._gpu_type = self._gl.glGetString(self._gl.GL_RENDERER)
        except UnicodeDecodeError:
            Logger.log("e", "DecodeError while getting GL_RENDERER via glGetString!")
            self._gpu_type = "Unknown"

        if not self.hasFrameBufferObjects():
            Logger.log("w", "No frame buffer support, falling back to texture copies.")

        Logger.log("d", "Initialized OpenGL subsystems.")
        Logger.log("d", "OpenGL Version:  %s", self._gl.glGetString(self._gl.GL_VERSION))
        Logger.log("d", "OpenGL Vendor:   %s", self._gl.glGetString(self._gl.GL_VENDOR))
        Logger.log("d", "OpenGL Renderer: %s", self._gpu_type)

    ##  Check if the current OpenGL implementation supports FrameBuffer Objects.
    #
    #   \return True if FBOs are supported, False if not.
    def hasFrameBufferObjects(self):
        return QOpenGLFramebufferObject.hasOpenGLFramebufferObjects()

    ##  Get the current GPU vendor.
    #
    #   \return One of the items of OpenGL.Vendor.
    def getGPUVendor(self):
        return self._gpu_vendor

    ##  Get a string describing the current GPU type.
    #
    #   This effectively should return the OpenGL renderer string.
    def getGPUType(self):
        return self._gpu_type

    ##  Get the OpenGL bindings object.
    #
    #   This should return an object that has all supported OpenGL functions
    #   as methods and additionally defines all OpenGL constants. This object
    #   is used to make direct OpenGL calls so should match OpenGL as closely
    #   as possible.
    def getBindingsObject(self):
        return self._gl

    ##  Create a FrameBuffer Object.
    #
    #   This should return an implementation-specifc FrameBufferObject subclass.
    def createFrameBufferObject(self, width, height):
        return FrameBufferObject.FrameBufferObject(width, height)

    ##  Create a Texture Object.
    #
    #   This should return an implementation-specifc Texture subclass.
    def createTexture(self):
        return Texture.Texture(self._gl)

    ##  Create a ShaderProgram Object.
    #
    #   This should return an implementation-specifc ShaderProgram subclass.
    def createShaderProgram(self, file_name):
        shader = ShaderProgram.ShaderProgram()
        # The version_string must match the keys in shader files.
        if OpenGLContext.isLegacyOpenGL():
            version_string = ""  # Nothing is added to "fragment" and "vertex"
        else:
            version_string = "41core"

        try:
            shader.load(file_name, version=version_string)
        except InvalidShaderProgramError:
            # If the loading failed, it could be that there is no specific shader for this version.
            # Try again without a version nr to get the generic one.
            if version_string != "":
                shader.load(file_name, version = "")
        return shader

    ##  Create a Vertex buffer for a mesh.
    #
    #   This will create a vertex buffer object that is filled with the
    #   vertex data of the mesh.
    #
    #   By default, the associated vertex buffer should be cached using a
    #   custom property on the mesh. This should use the VertexBufferProperty
    #   property name.
    #
    #   \param mesh The mesh to create a vertex buffer for.
    #   \param kwargs Keyword arguments.
    #                 Possible values:
    #                 - force_recreate: Ignore the cached value if set and always create a new buffer.
    def createVertexBuffer(self, mesh, **kwargs):
        if not kwargs.get("force_recreate", False) and hasattr(mesh, OpenGL.VertexBufferProperty):
            return getattr(mesh, OpenGL.VertexBufferProperty)

        buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        buffer.create()
        buffer.bind()

        float_size = ctypes.sizeof(ctypes.c_float)
        int_size = ctypes.sizeof(ctypes.c_int)

        buffer_size = mesh.getVertexCount() * 3 * float_size # Vertex count * number of components * sizeof(float32)
        if mesh.hasNormals():
            buffer_size += mesh.getVertexCount() * 3 * float_size # Vertex count * number of components * sizeof(float32)
        if mesh.hasColors():
            buffer_size += mesh.getVertexCount() * 4 * float_size # Vertex count * number of components * sizeof(float32)
        if mesh.hasUVCoordinates():
            buffer_size += mesh.getVertexCount() * 2 * float_size # Vertex count * number of components * sizeof(float32)
        for attribute_name in mesh.attributeNames():
            attribute = mesh.getAttribute(attribute_name)
            if attribute["opengl_type"] == "vector2f":
                buffer_size += mesh.getVertexCount() * 2 * float_size
            elif attribute["opengl_type"] == "vector4f":
                buffer_size += mesh.getVertexCount() * 4 * float_size
            elif attribute["opengl_type"] == "int":
                buffer_size += mesh.getVertexCount() * int_size
            elif attribute["opengl_type"] == "float":
                buffer_size += mesh.getVertexCount() * float_size
            else:
                Logger.log(
                    "e", "Could not determine buffer size for attribute [%s] with type [%s]" % (attribute_name, attribute["opengl_type"]))
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

        for attribute_name in mesh.attributeNames():
            attribute = mesh.getAttribute(attribute_name)
            attribute_byte_array = attribute["value"].tostring()
            buffer.write(offset, attribute_byte_array, len(attribute_byte_array))
            offset += len(attribute_byte_array)

        buffer.release()

        setattr(mesh, OpenGL.VertexBufferProperty, buffer)
        return buffer

    ##  Create an index buffer for a mesh.
    #
    #   This will create an index buffer object that is filled with the
    #   index data of the mesh.
    #
    #   By default, the associated index buffer should be cached using a
    #   custom property on the mesh. This should use the IndexBufferProperty
    #   property name.
    #
    #   \param mesh The mesh to create an index buffer for.
    #   \param kwargs Keyword arguments.
    #                 Possible values:
    #                 - force_recreate: Ignore the cached value if set and always create a new buffer.
    def createIndexBuffer(self, mesh, **kwargs):
        if not mesh.hasIndices():
            return None

        if not kwargs.get("force_recreate", False) and hasattr(mesh, OpenGL.IndexBufferProperty):
            return getattr(mesh, OpenGL.IndexBufferProperty)

        buffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        buffer.create()
        buffer.bind()

        data = mesh.getIndicesAsByteArray()
        if 'index_start' in kwargs and 'index_stop' in kwargs:
            buffer.allocate(data[4 * kwargs['index_start']:4 * kwargs['index_stop']], 4*(kwargs['index_stop'] - kwargs['index_start']))
        else:
            buffer.allocate(data, len(data))
        buffer.release()

        setattr(mesh, OpenGL.IndexBufferProperty, buffer)
        return buffer


    ##  Get the singleton instance.
    #
    #   \return The singleton instance.
    @classmethod
    def getInstance(cls) -> "OpenGL":
        return cls._instance

    ##  Set the singleton instance.
    #
    #   This is mostly meant to simplify the singleton logic and should be called
    #   by the OpenGL implementation as soon as possible.
    @classmethod
    def setInstance(cls, instance):
        cls._instance = instance

    ## private:
    _instance = None    # type: OpenGL
