# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QVector2D, QVector3D, QVector4D, QMatrix4x4, QColor, QImage, QOpenGLTexture
from UM.Logger import Logger
from UM.Application import Application

from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Math.Color import Color

from UM.View.GL.OpenGL import OpenGL
from UM.View.GL.ShaderProgram import ShaderProgram

##  Shader program subclass using PyQt for the OpenGL implementation.
class QtShaderProgram(ShaderProgram):
    def __init__(self):
        super().__init__()

        self._shader_program = None
        self._uniform_indices = {}
        self._attribute_indices = {}
        self._uniform_values = {}
        self._bound = False
        self._textures = {}

    def setVertexShader(self, shader):
        if not self._shader_program:
            self._shader_program = QOpenGLShaderProgram()

        if not self._shader_program.addShaderFromSourceCode(QOpenGLShader.Vertex, shader):
            Logger.log("e", "Vertex shader failed to compile: %s", self._shader_program.log())

    def setFragmentShader(self, shader):
        if not self._shader_program:
            self._shader_program = QOpenGLShaderProgram()

        if not self._shader_program.addShaderFromSourceCode(QOpenGLShader.Fragment, shader):
            Logger.log("e", "Fragment shader failed to compile: %s", self._shader_program.log())

    def build(self):
        if not self._shader_program:
            Logger.log("e", "No shader sources loaded")
            return

        if not self._shader_program.link():
            Logger.log("e", "Shader failed to link: %s", self._shader_program.log())

    def setUniformValue(self, name, value, **kwargs):
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
        if texture is None:
            if texture_unit in self._textures:
                del self._textures[texture_unit]
        else:
            self._textures[texture_unit] = texture

    def enableAttribute(self, name, type, offset, stride = 0):
        if not self._shader_program:
            return

        self.bind()

        if name not in self._attribute_indices:
            self._attribute_indices[name] = self._shader_program.attributeLocation(name)

        attribute = self._attribute_indices[name]
        if attribute == -1:
            return

        if type is "int":
            self._shader_program.setAttributeBuffer(attribute, 0x1404, offset, 1, stride) #GL_INT
        elif type is "float":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 1, stride) #GL_FLOAT
        elif type is "vector2f":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 2, stride) #GL_FLOAT
        elif type is "vector3f":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 3, stride) #GL_FLOAT
        elif type is "vector4f":
            self._shader_program.setAttributeBuffer(attribute, 0x1406, offset, 4, stride) #GL_FLOAT

        self._shader_program.enableAttributeArray(attribute)


    def disableAttribute(self, name):
        if not self._shader_program:
            return

        if name not in self._attribute_indices:
            return

        self._shader_program.disableAttributeArray(self._attribute_indices[name])

    def bind(self):
        if not self._shader_program or not self._shader_program.isLinked():
            return

        if self._bound:
            return

        self._bound = True
        self._shader_program.bind()

        for uniform in self._uniform_values:
            self._setUniformValueDirect(uniform, self._uniform_values[uniform])

        for texture_unit, texture in self._textures.items():
            texture.bind(texture_unit)

    def release(self):
        if not self._shader_program or not self._bound:
            return

        self._bound = False
        self._shader_program.release()

        for texture_unit, texture in self._textures.items():
            texture.release(texture_unit)

    def _matrixToQMatrix4x4(self, m):
        return QMatrix4x4(m.at(0,0), m.at(0, 1), m.at(0, 2), m.at(0, 3),
                          m.at(1,0), m.at(1, 1), m.at(1, 2), m.at(1, 3),
                          m.at(2,0), m.at(2, 1), m.at(2, 2), m.at(2, 3),
                          m.at(3,0), m.at(3, 1), m.at(3, 2), m.at(3, 3))

    def _setUniformValueDirect(self, uniform, value):
        if type(value) is Vector:
            self._shader_program.setUniformValue(uniform, QVector3D(value.x, value.y, value.z))
        elif type(value) is Matrix:
            self._shader_program.setUniformValue(uniform, self._matrixToQMatrix4x4(value))
        elif type(value) is Color:
            self._shader_program.setUniformValue(uniform, QColor(value.r * 255, value.g * 255, value.b * 255, value.a * 255))
        elif type(value) is list and len(value) is 2:
            self._shader_program.setUniformValue(uniform, QVector2D(value[0], value[1]))
        elif type(value) is list and len(value) is 3:
            self._shader_program.setUniformValue(uniform, QVector3D(value[0], value[1], value[2]))
        elif type(value) is list and len(value) is 4:
            self._shader_program.setUniformValue(uniform, QVector4D(value[0], value[1], value[2], value[3]))
        elif type(value) is list and type(value[0]) is list and len(value[0]) is 2:
            self._shader_program.setUniformValueArray(uniform, [QVector2D(i[0], i[1]) for i in value])
        else:
            self._shader_program.setUniformValue(uniform, value)

