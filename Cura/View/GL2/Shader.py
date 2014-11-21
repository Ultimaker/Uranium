from OpenGL.GL import *

from Cura.Math.Vector import Vector
from Cura.Math.Quaternion import Quaternion
from Cura.Math.Matrix import Matrix

from ctypes import c_void_p

##  Wrapper around an OpenGL shader program.
#   This class wraps an OpenGL shader program and the shaders it contains. Currently only
#   vertex and fragment shaders are supported.
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

    ##  Set the source code for the vertex shader.
    #   \param source The source code to use.
    def setVertexSource(self, source):
        self._vertexSource = source

    ##  Set the source code for the fragment shader.
    #   \param source The source code to use.
    def setFragmentSource(self, source):
        self._fragmentSource = source

    ##  Compile and link the shader program.
    #   This will create the actual OpenGL shaders and program and use
    #   the set vertex and fragment sources to compile and link the program.
    #   It does nothing if vertex or fragment source is not set.
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

    ##  Bind the shader program so it can be used for rendering.
    def bind(self):
        if not self._bound:
            glUseProgram(self._program)
            self._bound = True

    ##  Release the shader program. Does nothing if the shader was not bound in the first place.
    def release(self):
        if self._bound:
            glUseProgram(0)
            self._bound = False

    ##  Set a uniform value.
    #   \param name The name of the uniform to set.
    #   \param value The value to set the uniform to. Recognised types are int, float, Vector, Quaternion and Matrix.
    #   \note This will bind the shader if it was not already bound, clearing any previous shader binding.
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

    ##  Bind a vertex attribute to the current shader.
    #   \param name The name of the attribute.
    #   \param components The number of components for each entry in the attribute array. For example, this is 3 for a 3-dimensional vector.
    #   \param type The type of the attribute. Should be one of the OpenGL type constants like GL_FLOAT.
    #   \param offset The offset into the current bound buffer object where this attribute starts.
    def bindAttribute(self, name, components, type, offset):
        self.bind()
        if name not in self._attributeLocations:
            loc = glGetAttribLocation(self._program, name)
            self._attributeLocations[name] = loc

        loc = self._attributeLocations[name]
        glEnableVertexAttribArray(loc)
        glVertexAttribPointer(loc, components, type, False, 0, c_void_p(offset))

    ##  Release a bound vertex attribute.
    #   \param name The name of the attribute to release.
    def releaseAttribute(self, name):
        if name not in self._attributeLocations:
            return #It was never bound in the first place, so just ignore

        glDisableVertexAttribArray(self._attributeLocations[name])
