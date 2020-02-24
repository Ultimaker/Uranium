# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import sys
import ctypes   # type: ignore

from PyQt5.QtGui import QOpenGLVersionProfile, QOpenGLContext, QOpenGLFramebufferObject, QOpenGLBuffer
from PyQt5.QtWidgets import QMessageBox
from typing import Any, TYPE_CHECKING, cast

from UM.Logger import Logger

from UM.Version import Version
from UM.View.GL.FrameBufferObject import FrameBufferObject
from UM.View.GL.ShaderProgram import ShaderProgram
from UM.View.GL.ShaderProgram import InvalidShaderProgramError
from UM.View.GL.Texture import Texture
from UM.View.GL.OpenGLContext import OpenGLContext
from UM.i18n import i18nCatalog  # To make dialogs translatable.
i18n_catalog = i18nCatalog("uranium")

if TYPE_CHECKING:
    from UM.Mesh.MeshData import MeshData


class OpenGL:
    """Convenience methods for dealing with OpenGL.

    This class simplifies dealing with OpenGL and different Python OpenGL bindings. It
    mostly describes an interface that should be implemented for dealing with basic OpenGL
    functionality using these different OpenGL bindings. Additionally, it provides singleton
    handling. The implementation-defined subclass must be set as singleton instance as soon
    as possible so that any calls to getInstance() return a proper object.
    """
    VertexBufferProperty = "__vertex_buffer"
    IndexBufferProperty = "__index_buffer"

    class Vendor:
        """Different OpenGL chipset vendors."""
        NVidia = 1
        AMD = 2
        Intel = 3
        Other = 4

    def __init__(self) -> None:
        if OpenGL.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        OpenGL.__instance = self

        super().__init__()

        profile = QOpenGLVersionProfile()
        profile.setVersion(OpenGLContext.major_version, OpenGLContext.minor_version)
        profile.setProfile(OpenGLContext.profile)

        context = QOpenGLContext.currentContext()
        if not context:
            Logger.log("e", "Startup failed due to OpenGL context creation failing")
            QMessageBox.critical(None, i18n_catalog.i18nc("@message", "Failed to Initialize OpenGL", "Could not initialize an OpenGL context. This program requires OpenGL 2.0 or higher. Please check your video card drivers."))
            sys.exit(1)
        self._gl = context.versionFunctions(profile) # type: Any #It's actually a protected class in PyQt that depends on the implementation of your graphics card.
        if not self._gl:
            Logger.log("e", "Startup failed due to OpenGL initialization failing")
            QMessageBox.critical(None, i18n_catalog.i18nc("@message", "Failed to Initialize OpenGL", "Could not initialize OpenGL. This program requires OpenGL 2.0 or higher. Please check your video card drivers."))
            sys.exit(1)

        # It would be nice to be able to not necessarily need OpenGL FrameBuffer Object support, but
        # due to a limitation in PyQt, currently glReadPixels or similar methods are not available.
        # This means we can only get frame buffer contents through methods that indirectly call
        # those methods, in this case primarily QOpenGLFrameBufferObject::toImage(), making us
        # hard-depend on FrameBuffer Objects.
        if not self.hasFrameBufferObjects():
            Logger.log("e", "Startup failed, OpenGL does not support Frame Buffer Objects")
            QMessageBox.critical(None, i18n_catalog.i18nc("Critical OpenGL Extensions Missing", "Critical OpenGL extensions are missing. This program requires support for Framebuffer Objects. Please check your video card drivers."))
            sys.exit(1)

        self._gl.initializeOpenGLFunctions()

        self._gpu_vendor = OpenGL.Vendor.Other #type: int
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

        self._gpu_type = "Unknown"  # type: str
        # WORKAROUND: Cura/#1117 Cura-packaging/12
        # Some Intel GPU chipsets return a string, which is not undecodable via PyQt5.
        # This workaround makes the code fall back to a "Unknown" renderer in these cases.
        try:
            self._gpu_type = self._gl.glGetString(self._gl.GL_RENDERER)
        except UnicodeDecodeError:
            Logger.log("e", "DecodeError while getting GL_RENDERER via glGetString!")

        self._opengl_version = self._gl.glGetString(self._gl.GL_VERSION) #type: str

        self._opengl_shading_language_version = Version("0.0")  # type: Version
        try:
            self._opengl_shading_language_version = Version(self._gl.glGetString(self._gl.GL_SHADING_LANGUAGE_VERSION))
        except:
            self._opengl_shading_language_version = Version("1.0")

        if not self.hasFrameBufferObjects():
            Logger.log("w", "No frame buffer support, falling back to texture copies.")

        Logger.log("d", "Initialized OpenGL subsystems.")
        Logger.log("d", "OpenGL Version:  %s", self._opengl_version)
        Logger.log("d", "OpenGL Vendor:   %s", self._gl.glGetString(self._gl.GL_VENDOR))
        Logger.log("d", "OpenGL Renderer: %s", self._gpu_type)
        Logger.log("d", "GLSL Version:    %s", self._opengl_shading_language_version)

    def hasFrameBufferObjects(self) -> bool:
        """Check if the current OpenGL implementation supports FrameBuffer Objects.

        :return: True if FBOs are supported, False if not.
        """
        return QOpenGLFramebufferObject.hasOpenGLFramebufferObjects()

    def getOpenGLVersion(self) -> str:
        """Get the current OpenGL version.

        :return: Version of OpenGL
        """
        return self._opengl_version

    def getOpenGLShadingLanguageVersion(self) -> "Version":
        """Get the current OpenGL shading language version.

        :return: Shading language version of OpenGL
        """
        return self._opengl_shading_language_version

    def getGPUVendorName(self) -> str:
        """Get the current GPU vendor name.

        :return: Name of the vendor of current GPU
        """
        return self._gl.glGetString(self._gl.GL_VENDOR)

    def getGPUVendor(self) -> int:
        """Get the current GPU vendor.

        :return: One of the items of OpenGL.Vendor.
        """
        return self._gpu_vendor

    def getGPUType(self) -> str:
        """Get a string describing the current GPU type.

        This effectively should return the OpenGL renderer string.
        """
        return self._gpu_type

    def getBindingsObject(self) -> Any:
        """Get the OpenGL bindings object.

        This should return an object that has all supported OpenGL functions
        as methods and additionally defines all OpenGL constants. This object
        is used to make direct OpenGL calls so should match OpenGL as closely
        as possible.
        """
        return self._gl

    def createFrameBufferObject(self, width: int, height: int) -> FrameBufferObject:
        """Create a FrameBuffer Object.

        This should return an implementation-specifc FrameBufferObject subclass.
        """
        return FrameBufferObject(width, height)

    def createTexture(self) -> Texture:
        """Create a Texture Object.

        This should return an implementation-specific Texture subclass.
        """
        return Texture(self._gl)

    def createShaderProgram(self, file_name: str) -> ShaderProgram:
        """Create a ShaderProgram Object.

        This should return an implementation-specifc ShaderProgram subclass.
        """
        shader = ShaderProgram()
        # The version_string must match the keys in shader files.
        if OpenGLContext.isLegacyOpenGL():
            version_string = ""  # Nothing is added to "fragment" and "vertex"
        else:
            version_string = "41core"

        try:
            shader.load(file_name, version = version_string)
        except InvalidShaderProgramError:
            # If the loading failed, it could be that there is no specific shader for this version.
            # Try again without a version nr to get the generic one.
            if version_string != "":
                shader.load(file_name, version = "")
        return shader

    def createVertexBuffer(self, mesh: "MeshData", **kwargs: Any) -> QOpenGLBuffer:
        """Create a Vertex buffer for a mesh.

        This will create a vertex buffer object that is filled with the
        vertex data of the mesh.

        By default, the associated vertex buffer should be cached using a
        custom property on the mesh. This should use the VertexBufferProperty
        property name.

        :param mesh: The mesh to create a vertex buffer for.
        :param kwargs: Keyword arguments.
        Possible values:
        - force_recreate: Ignore the cached value if set and always create a new buffer.
        """
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
            normals = cast(bytes, mesh.getNormalsAsByteArray())
            buffer.write(offset, normals, len(normals))
            offset += len(normals)

        if mesh.hasColors():
            colors = cast(bytes, mesh.getColorsAsByteArray())
            buffer.write(offset, colors, len(colors))
            offset += len(colors)

        if mesh.hasUVCoordinates():
            uvs = cast(bytes, mesh.getUVCoordinatesAsByteArray())
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

    def createIndexBuffer(self, mesh: "MeshData", **kwargs: Any):
        """Create an index buffer for a mesh.

        This will create an index buffer object that is filled with the
        index data of the mesh.

        By default, the associated index buffer should be cached using a
        custom property on the mesh. This should use the IndexBufferProperty
        property name.

        :param mesh: The mesh to create an index buffer for.
        :param kwargs: Keyword arguments.
            Possible values:
            - force_recreate: Ignore the cached value if set and always create a new buffer.
        """
        if not mesh.hasIndices():
            return None

        if not kwargs.get("force_recreate", False) and hasattr(mesh, OpenGL.IndexBufferProperty):
            return getattr(mesh, OpenGL.IndexBufferProperty)

        buffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        buffer.create()
        buffer.bind()

        data = cast(bytes, mesh.getIndicesAsByteArray()) # We check for None at the beginning of the method
        if 'index_start' in kwargs and 'index_stop' in kwargs:
            buffer.allocate(data[4 * kwargs['index_start']:4 * kwargs['index_stop']], 4*(kwargs['index_stop'] - kwargs['index_start']))
        else:
            buffer.allocate(data, len(data))
        buffer.release()

        setattr(mesh, OpenGL.IndexBufferProperty, buffer)

        return buffer

    __instance = None    # type: OpenGL

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "OpenGL":
        return cls.__instance
