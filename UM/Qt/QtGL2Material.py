from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QVector2D, QVector3D, QVector4D, QMatrix4x4, QColor, QImage, QOpenGLTexture
from UM.View.Material import Material
from UM.Logger import Logger

from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Math.Color import Color

class QtGL2Material(Material):
    def __init__(self, renderer):
        super().__init__()

        self._gl = renderer._gl

        self._shader_program = None
        self._uniform_indices = {}
        self._attribute_indices = {}
        self._uniform_values = {}
        self._bound = False
        self._textures = {}

    def loadVertexShader(self, file):
        if not self._shader_program:
            self._shader_program = QOpenGLShaderProgram()

        self._shader_program.addShaderFromSourceFile(QOpenGLShader.Vertex, file)

    def loadFragmentShader(self, file):
        if not self._shader_program:
            self._shader_program = QOpenGLShaderProgram()

        self._shader_program.addShaderFromSourceFile(QOpenGLShader.Fragment, file)

    def build(self):
        if not self._shader_program:
            Logger.log('e', 'No shader sources loaded')
            return

        self._shader_program.link()

    def setUniformValue(self, name, value, **kwargs):
        if not self._shader_program:
            return

        cache = True
        if 'cache' in kwargs:
            cache = kwargs['cache']

        if not name in self._uniform_indices:
            self._uniform_indices[name] = self._shader_program.uniformLocation(name)

        uniform = self._uniform_indices[name]
        if uniform == -1:
            return

        if cache:
            self._uniform_values[uniform] = value

        if self._bound:
            self._setUniformValueDirect(uniform, value)

    def setUniformTexture(self, name, file):
        if not self._shader_program:
            return

        if not name in self._uniform_indices:
            self._uniform_indices[name] = self._shader_program.uniformLocation(name)

        index = self._uniform_indices[name]

        texture = QOpenGLTexture(QImage(file).mirrored())
        texture.setMinMagFilters(QOpenGLTexture.Linear, QOpenGLTexture.Linear)
        self._textures[index] = texture

        self._uniform_values[index] = 1

        if self._bound:
            texture = self._textures[index]
            texture.bind()
            self._setUniformValueDirect(index, texture.textureId())

    def enableAttribute(self, name, type, offset, stride = 0):
        if not self._shader_program:
            return

        self.bind()

        if not name in self._attribute_indices:
            self._attribute_indices[name] = self._shader_program.attributeLocation(name)

        attribute = self._attribute_indices[name]
        if attribute == -1:
            return

        if type is 'int':
            self._shader_program.setAttributeBuffer(attribute, self._gl.GL_INT, offset, 1, stride)
        elif type is 'float':
            self._shader_program.setAttributeBuffer(attribute, self._gl.GL_FLOAT, offset, 1, stride)
        elif type is 'vector2f':
            self._shader_program.setAttributeBuffer(attribute, self._gl.GL_FLOAT, offset, 2, stride)
        elif type is 'vector3f':
            self._shader_program.setAttributeBuffer(attribute, self._gl.GL_FLOAT, offset, 3, stride)
        elif type is 'vector4f':
            self._shader_program.setAttributeBuffer(attribute, self._gl.GL_FLOAT, offset, 4, stride)

        self._shader_program.enableAttributeArray(attribute)


    def disableAttribute(self, name):
        if not self._shader_program:
            return

        if not name in self._attribute_indices:
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
            if uniform in self._textures:
                texture = self._textures[uniform]
                texture.bind()
                self._setUniformValueDirect(uniform, 0)
            else:
                self._setUniformValueDirect(uniform, self._uniform_values[uniform])

    def release(self):
        if not self._shader_program or not self._bound:
            return

        for texture in self._textures.values():
            texture.release()

        self._bound = False
        self._shader_program.release()

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
        else:
            self._shader_program.setUniformValue(uniform, value)

