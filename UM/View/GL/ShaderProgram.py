# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser

class InvalidShaderProgramError(Exception):
    pass

class ShaderProgram:
    def __init__(self):
        self._bindings = {}
        self._attribute_bindings = {}

    def load(self, file_name):
        parser = configparser.ConfigParser()
        parser.read(file_name)

        if not "shaders" in parser:
            raise InvalidShaderProgramError("{0} is missing a vertex of fragment shader".format(file_name))

        if not "vertex" in parser["shaders"] or not "fragment" in parser["shaders"]:
            raise InvalidShaderProgramError("{0} is missing a vertex of fragment shader".format(file_name))

        self.setVertexShader(parser["shaders"]["vertex"])
        self.setFragmentShader(parser["shaders"]["fragment"])

        if "defaults" in parser:
            for key, value in parser["defaults"].items():
                self.setUniformValue(key, value, cache = True)

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
        raise NotImplementedError()

    ##  Load the fragment shader from a file.
    #
    #   \param shader \type{string} The fragment shader to use.
    def setFragmentShader(self, shader):
        raise NotImplementedError()

    ##  Build the complete shader program out of the separately loaded sources.
    def build(self):
        raise NotImplementedError()

    ##  Set a named uniform variable.
    #
    #   \param name The name of the uniform variable.
    #   \param value The value to set the variable to.
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - cache: False when the value should not be cached for later calls to bind().
    def setUniformValue(self, name, value, **kwargs):
        raise NotImplementedError()

    ##  Enable a vertex attribute to be used.
    #
    #   \param name The name of the attribute to enable.
    #   \param type The type of the attribute. Should be a python type.
    #   \param offset The offset into a bound buffer where the data for this attribute starts.
    #   \param stride The stride of the attribute.
    #
    #   \note If the material is not bound, this will bind the material.
    def enableAttribute(self, name, type, offset, stride = 0):
        raise NotImplementedError()

    ##  Disable a vertex attribute so it is no longer used.
    #
    #   \param name The name of the attribute to use.
    def disableAttribute(self, name):
        raise NotImplementedError()

    ##  Bind the material to use it for rendering.
    def bind(self):
        raise NotImplementedError()

    ##  Release the material so it will no longer be used for rendering.
    def release(self):
        raise NotImplementedError()

    def addBinding(self, key, value):
        self._bindings[key] = value

    def removeBinding(self, key):
        if key not in self._bindings:
            return

        del self._bindings[key]

    def updateBindings(self, state):
        for uniform, binding in self._bindings.items():
            if binding in state:
                self.setUniformValue(uniform, state[binding], cache = False)

    def addAttributeBinding(self, key, value):
        self._attribute_bindings[key] = value

    def removeAttributeBinding(self, key):
        if key not in self._attribute_bindings:
            return

        self._attribute_bindings.remove(key)
