# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import configparser
import ast

from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QVector2D, QVector3D, QVector4D, QMatrix4x4, QColor
from UM.Logger import Logger

from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Math.Color import Color


class InvalidShaderProgramError(Exception):
    """Raised when an error occurs during loading of the shader file."""
    pass


class ShaderProgram:
    """An abstract class for dealing with shader programs.

    This class provides an interface an some basic elements for dealing with
    shader programs. Shader programs are described in a simple text file
    based on the Python configparser module. These files contain the shaders
    for the different shader program stages, in addition to defaults that should
    be used for uniform values and uniform and attribute bindings.
    """
    def __init__(self):
        self._bindings = {}
        self._attribute_bindings = {}

        self._shader_program = None
        self._uniform_indices = {}
        self._attribute_indices = {}
        self._uniform_values = {}
        self._bound = False
        self._textures = {}

        self._debug_shader = False  # Set this to true to enable extra logging concerning shaders

    def load(self, file_name, version = ""):
        """Load a shader program file.

        This method loads shaders from a simple text file, using Python's configparser
        as parser.

        :note When writing shader program files, please note that configparser expects
        indented lines for multiline values. Since the shaders are provided as a single
        multiline string, make sure to indent them properly.

        :param file_name: The shader file to load.
        :param version: can be used for a special version of the shader. it will be appended
        to the keys [vertex, fragment, geometry] in the shader file

        :exception{InvalidShaderProgramError} Raised when the file provided does not contain any valid shaders.
        """
        Logger.log("d", "Loading shader file [%s]...", file_name)

        vertex_key = "vertex" + version
        fragment_key = "fragment" + version
        geometry_key = "geometry" + version

        # Hashtags should not be ignored, they are part of GLSL.
        parser = configparser.ConfigParser(interpolation = None, comment_prefixes = (';', ))
        parser.optionxform = lambda option: option
        parser.read(file_name)

        if "shaders" not in parser:
            raise InvalidShaderProgramError("{0} is missing section [shaders]".format(file_name))

        if vertex_key not in parser["shaders"] or fragment_key not in parser["shaders"]:
            raise InvalidShaderProgramError("{0} is missing a shader [{1}, {2}]".format(file_name, vertex_key, fragment_key))

        vertex_code = parser["shaders"][vertex_key]
        if self._debug_shader:
            vertex_code_str = "\n".join(["%4i %s" % (i, s) for i, s in enumerate(vertex_code.split("\n"))])
            Logger.log("d", "Vertex shader")
            Logger.log("d", vertex_code_str)

        fragment_code = parser["shaders"][fragment_key]
        if self._debug_shader:
            fragment_code_str = "\n".join(["%4i %s" % (i, s) for i, s in enumerate(fragment_code.split("\n"))])
            Logger.log("d", "Fragment shader")
            Logger.log("d", fragment_code_str)

        self.setVertexShader(vertex_code)
        self.setFragmentShader(fragment_code)
        # Geometry shader is optional and only since version OpenGL 3.2 or with extension ARB_geometry_shader4
        if geometry_key in parser["shaders"]:
            code = parser["shaders"][geometry_key]
            if self._debug_shader:
                code_str = "\n".join(["%4i %s" % (i, s) for i, s in enumerate(code.split("\n"))])
                Logger.log("d", "Loading geometry shader... \n")
                Logger.log("d", code_str)
            self.setGeometryShader(code)

        self.build()

        if "defaults" in parser:
            for key, value in parser["defaults"].items():
                self.setUniformValue(key, ast.literal_eval(value), cache = True)

        if "bindings" in parser:
            for key, value in parser["bindings"].items():
                self.addBinding(key, value)

        if "attributes" in parser:
            for key, value in parser["attributes"].items():
                self.addAttributeBinding(key, value)

    def setVertexShader(self, shader):
        """Set the vertex shader to use.

        :param shader: :type{string} The vertex shader to use.
        """
        if not self._shader_program:
            self._shader_program = QOpenGLShaderProgram()

        if not self._shader_program.addShaderFromSourceCode(QOpenGLShader.Vertex, shader):
            Logger.log("e", "Vertex shader failed to compile: %s", self._shader_program.log())

    def setFragmentShader(self, shader):
        """Set the fragment shader to use.

        :param shader: :type{string} The fragment shader to use.
        """
        if not self._shader_program:
            self._shader_program = QOpenGLShaderProgram()

        if not self._shader_program.addShaderFromSourceCode(QOpenGLShader.Fragment, shader):
            Logger.log("e", "Fragment shader failed to compile: %s", self._shader_program.log())

    def setGeometryShader(self, shader):
        if not self._shader_program:
            self._shader_program = QOpenGLShaderProgram()

        if not self._shader_program.addShaderFromSourceCode(QOpenGLShader.Geometry, shader):
            Logger.log("e", "Geometry shader failed to compile: %s", self._shader_program.log())

    def build(self):
        """Build the complete shader program out of the separately provided sources."""
        if not self._shader_program:
            Logger.log("e", "No shader sources loaded")
            return

        if not self._shader_program.link():
            Logger.log("e", "Shader failed to link: %s", self._shader_program.log())

    def setUniformValue(self, name, value, **kwargs):
        """Set a named uniform variable.

        Unless otherwise specified as argument, the specified value will be cached so that
        it does not matter whether bind() has already been called. Instead, if the shader
        is not currently bound, the next call to bind() will update the uniform values.

        :param name: The name of the uniform variable.
        :param value: The value to set the variable to.
        :param kwargs: Keyword arguments.
        Possible keywords:
        - cache: False when the value should not be cached for later calls to bind().
        """
        if not self._shader_program:
            return

        if name not in self._uniform_indices:
            self._uniform_indices[name] = self._shader_program.uniformLocation(name)

        uniform = self._uniform_indices[name]
        if uniform == -1:
            return

        if kwargs.get("cache", True):
            self._uniform_values[uniform] = value

        if self._bound:
            self._setUniformValueDirect(uniform, value)

    def setTexture(self, texture_unit, texture):
        """Set a texture that should be bound to a specified texture unit when this shader is bound.

        :param texture_unit: :type{int} The texture unit to bind the texture to.
        :param texture: :type{Texture} The texture object to bind to the texture unit.
        """
        if texture is None:
            if texture_unit in self._textures:
                del self._textures[texture_unit]
        else:
            self._textures[texture_unit] = texture

    def enableAttribute(self, name: str, type: str, offset: int, stride: int = 0) -> None:
        """Enable a vertex attribute to be used.

        :param name: The name of the attribute to enable.
        :param type: The type of the attribute. Should be a python type.
        :param offset: The offset into a bound buffer where the data for this attribute starts.
        :param stride: The stride of the attribute.

        :note If the shader is not bound, this will bind the shader.
        """
        self.bind()

        if name not in self._attribute_indices:
            self._attribute_indices[name] = self._shader_program.attributeLocation(name)

        attribute = self._attribute_indices[name]
        if attribute == -1:
            return

        if type == "vector3f":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 3, stride) #GL_FLOAT
        elif type == "vector2f":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 2, stride)  # GL_FLOAT
        elif type == "vector4f":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 4, stride)  # GL_FLOAT
        elif type == "int":
            self._shader_program.setAttributeBuffer(attribute, 0x1404, offset, 1, stride) #GL_INT
        elif type == "float":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 1, stride) #GL_FLOAT

        self._shader_program.enableAttributeArray(attribute)

    def disableAttribute(self, name: str) -> None:
        """Disable a vertex attribute so it is no longer used.

        :param name: The name of the attribute to use.
        """
        if not self._shader_program:
            return

        if name not in self._attribute_indices:
            return

        self._shader_program.disableAttributeArray(self._attribute_indices[name])

    def bind(self) -> None:
        """Bind the shader to use it for rendering."""
        if self._bound:
            return

        if not self._shader_program or not self._shader_program.isLinked():
            return

        self._shader_program.bind()
        self._bound = True

        for uniform in self._uniform_values:
            self._setUniformValueDirect(uniform, self._uniform_values[uniform])

        for texture_unit, texture in self._textures.items():
            texture.bind(texture_unit)

    def release(self) -> None:
        """Release the shader so it will no longer be used for rendering."""
        if not self._shader_program or not self._bound:
            return

        self._shader_program.release()
        self._bound = False

        for texture_unit, texture in self._textures.items():
            texture.release(texture_unit)

    def addBinding(self, key, value):
        """Add a uniform value binding.

        Uniform value bindings are used to provide an abstraction between uniforms as set
        from code and uniforms as used from shaders. Each binding specifies a uniform name
        as key that should be mapped to a string that can be used to look up the value of
        the uniform.

        :param key: The name of the uniform to bind.
        :param value: The string used to look up values for this uniform.
        """
        self._bindings[value] = key

    def removeBinding(self, key: str) -> None:
        """Remove a uniform value binding.

        :param key: The uniform to remove.
        """
        if key not in self._bindings:
            return

        del self._bindings[key]

    def updateBindings(self, **kwargs) -> None:
        """Update the values of bindings.

        :param kwargs: Keyword arguments.
        Each key should correspond to a binding name, with the
        value being the value of the uniform.

        :note By default, these values are not cached as they are expected to be continuously
        updated.
        """
        for key, value in kwargs.items():
            if key in self._bindings and value is not None:
                self.setUniformValue(self._bindings[key], value, cache = False)

    def addAttributeBinding(self, key, value):
        """Add an attribute binding.

        Attribute bindings are similar to uniform value bindings, except they specify what
        what attribute name binds to which attribute in the shader.

        TODO: Actually use these bindings. However, that kind of depends on a more freeform
        MeshData object as freeform bindings are rather useless when we only have 5 supported
        attributes.

        :param key: The identifier used in the shader for the attribute.
        :param value: The name to bind to this attribute.
        """
        self._attribute_bindings[key] = value

    def removeAttributeBinding(self, key: str) -> None:
        """Remove an attribute binding.

        :param key: The name of the attribute binding to remove.
        """
        if key not in self._attribute_bindings:
            return

        del self._attribute_bindings[key]

    def _matrixToQMatrix4x4(self, m):
        return QMatrix4x4(m.getData().flatten())

    def _setUniformValueDirect(self, uniform, value):
        if type(value) is Vector:
            self._shader_program.setUniformValue(uniform, QVector3D(value.x, value.y, value.z))
        elif type(value) is Matrix:
            self._shader_program.setUniformValue(uniform, self._matrixToQMatrix4x4(value))
        elif type(value) is Color:
            self._shader_program.setUniformValue(uniform,
                QColor(value.r * 255, value.g * 255, value.b * 255, value.a * 255))
        elif type(value) is list and type(value[0]) is list and len(value[0]) == 4:
            self._shader_program.setUniformValue(uniform, self._matrixToQMatrix4x4(Matrix(value)))
        elif type(value) is list and len(value) == 2:
            self._shader_program.setUniformValue(uniform, QVector2D(value[0], value[1]))
        elif type(value) is list and len(value) == 3:
            self._shader_program.setUniformValue(uniform, QVector3D(value[0], value[1], value[2]))
        elif type(value) is list and len(value) == 4:
            self._shader_program.setUniformValue(uniform, QVector4D(value[0], value[1], value[2], value[3]))
        elif type(value) is list and type(value[0]) is list and len(value[0]) == 2:
            self._shader_program.setUniformValueArray(uniform, [QVector2D(i[0], i[1]) for i in value])
        else:
            self._shader_program.setUniformValue(uniform, value)
