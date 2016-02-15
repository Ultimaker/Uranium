# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser
import ast

##  Raised when an error occurs during loading of the shader file.
class InvalidShaderProgramError(Exception):
    pass

##  An abstract class for dealing with shader programs.
#
#   This class provides an interface an some basic elements for dealing with
#   shader programs. Shader programs are described in a simple text file
#   based on the Python configparser module. These files contain the shaders
#   for the different shader program stages, in addition to defaults that should
#   be used for uniform values and uniform and attribute bindings.
class ShaderProgram:
    def __init__(self):
        self._bindings = {}
        self._attribute_bindings = {}

    ##  Load a shader program file.
    #
    #   This method loads shaders from a simple text file, using Python's configparser
    #   as parser.
    #
    #   \note When writing shader program files, please note that configparser expects
    #   indented lines for multiline values. Since the shaders are provided as a single
    #   multiline string, make sure to indent them properly.
    #
    #   \param file_name The shader file to load.
    #
    #   \exception{InvalidShaderProgramError} Raised when the file provided does not contain any valid shaders.
    def load(self, file_name):
        parser = configparser.ConfigParser(interpolation = None)
        parser.optionxform = lambda option: option
        parser.read(file_name)

        if "shaders" not in parser:
            raise InvalidShaderProgramError("{0} is missing a vertex of fragment shader".format(file_name))

        if "vertex" not in parser["shaders"] or "fragment" not in parser["shaders"]:
            raise InvalidShaderProgramError("{0} is missing a vertex of fragment shader".format(file_name))

        self.setVertexShader(parser["shaders"]["vertex"])
        self.setFragmentShader(parser["shaders"]["fragment"])

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

    ##  Set the vertex shader to use.
    #
    #   \param shader \type{string} The vertex shader to use.
    def setVertexShader(self, shader):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Set the fragment shader to use.
    #
    #   \param shader \type{string} The fragment shader to use.
    def setFragmentShader(self, shader):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Build the complete shader program out of the separately provided sources.
    def build(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Set a named uniform variable.
    #
    #   Unless otherwise specified as argument, the specified value will be cached so that
    #   it does not matter whether bind() has already been called. Instead, if the shader
    #   is not currently bound, the next call to bind() will update the uniform values.
    #
    #   \param name The name of the uniform variable.
    #   \param value The value to set the variable to.
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - cache: False when the value should not be cached for later calls to bind().
    def setUniformValue(self, name, value, **kwargs):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Set a texture that should be bound to a specified texture unit when this shader is bound.
    #
    #   \param texture_unit \type{int} The texture unit to bind the texture to.
    #   \param texture \type{Texture} The texture object to bind to the texture unit.
    def setTexture(self, texture_unit, texture):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Enable a vertex attribute to be used.
    #
    #   \param name The name of the attribute to enable.
    #   \param type The type of the attribute. Should be a python type.
    #   \param offset The offset into a bound buffer where the data for this attribute starts.
    #   \param stride The stride of the attribute.
    #
    #   \note If the shader is not bound, this will bind the shader.
    def enableAttribute(self, name, type, offset, stride = 0):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Disable a vertex attribute so it is no longer used.
    #
    #   \param name The name of the attribute to use.
    def disableAttribute(self, name):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Bind the shader to use it for rendering.
    def bind(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Release the shader so it will no longer be used for rendering.
    def release(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Add a uniform value binding.
    #
    #   Uniform value bindings are used to provide an abstraction between uniforms as set
    #   from code and uniforms as used from shaders. Each binding specifies a uniform name
    #   as key that should be mapped to a string that can be used to look up the value of
    #   the uniform.
    #
    #   \param key The name of the uniform to bind.
    #   \param value The string used to look up values for this uniform.
    def addBinding(self, key, value):
        self._bindings[value] = key

    ##  Remove a uniform value binding.
    #
    #   \param key The uniform to remove.
    def removeBinding(self, key):
        if key not in self._bindings:
            return

        del self._bindings[key]

    ##  Update the values of bindings.
    #
    #   \param kwargs Keyword arguments.
    #                 Each key should correspond to a binding name, with the
    #                 value being the value of the uniform.
    #
    #   \note By default, these values are not cached as they are expected to be continuously
    #         updated.
    def updateBindings(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._bindings and value is not None:
                self.setUniformValue(self._bindings[key], value, cache = False)

    ##  Add an attribute binding.
    #
    #   Attribute bindings are similar to uniform value bindings, except they specify what
    #   what attribute name binds to which attribute in the shader.
    #
    #   TODO: Actually use these bindings. However, that kind of depends on a more freeform
    #   MeshData object as freeform bindings are rather useless when we only have 5 supported
    #   attributes.
    #
    #   \param key The identifier used in the shader for the attribute.
    #   \param value The name to bind to this attribute.
    def addAttributeBinding(self, key, value):
        self._attribute_bindings[key] = value

    ##  Remove an attribute binding.
    #
    #   \param key The name of the attribute binding to remove.
    def removeAttributeBinding(self, key):
        if key not in self._attribute_bindings:
            return

        self._attribute_bindings.remove(key)
