from OpenGL.GL import *

from Cura.Math.Vector import Vector
from Cura.Math.Quaternion import Quaternion
from Cura.Math.Matrix import Matrix

from ctypes import c_void_p

class Shader(object):
    def __init__(self):
        super(Shader, self).__init__()
        self._vertexSource = None
        self._fragmentSource = None

        self._vertexShader = None
        self._fragmentShader = None
        self._program = None

        self._bound = False

        self._uniformLocations = {}
        self._attributeLocations = {}

    def setVertexSource(self, source):
        self._vertexSource = source

    def setFragmentSource(self, source):
        self._fragmentSource = source

    def build(self):
        if not self._vertexSource or not self._fragmentSource:
            return

        self._vertexShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self._vertexShader, self._vertexSource)
        glCompileShader(self._vertexShader)

        self._fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self._fragmentShader, self._fragmentSource)
        glCompileShader(self._fragmentShader)

        self._program = glCreateProgram()
        glAttachShader(self._program, self._vertexShader)
        glAttachShader(self._program, self._fragmentShader)
        glLinkProgram(self._program)

    def bind(self):
        if not self._bound:
            glUseProgram(self._program)
            self._bound = True

    def release(self):
        if self._bound:
            glUseProgram(0)
            self._bound = False

    def setUniform(self, name, value):
        self.bind()
        if name not in self._uniformLocations:
            loc = glGetUniformLocation(self._program, name)
            self._uniformLocations[name] = loc

        loc = self._uniformLocations[name]

        if type(value) is int:
            glUniform1i(loc, value)
        elif type(value) is float:
            glUniform1f(loc, value)
        elif type(value) is Vector:
            glUniform3f(loc, value.x, value.y, value.z)
        elif type(value) is Quaternion:
            glUniform4fv(loc, value.getData())
        elif type(value) is Matrix:
            glUniformMatrix4fv(loc, 1, False, value.getTransposed().getData())

    def bindAttribute(self, name, components, type, offset):
        self.bind()
        if name not in self._attributeLocations:
            loc = glGetAttribLocation(self._program, name)
            self._attributeLocations[name] = loc

        loc = self._attributeLocations[name]
        glEnableVertexAttribArray(loc)
        glVertexAttribPointer(loc, components, type, False, 0, c_void_p(offset))

    def releaseAttribute(self, name):
        if name not in self._attributeLocations:
            return #It was never bound in the first place, so just ignore

        glDisableVertexAttribArray(self._attributeLocations[name])
