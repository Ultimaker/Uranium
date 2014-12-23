class Material:
    def __init__(self):
        pass

    ##  Load the vertex shader from a file.
    #
    #   \param file \type{string} The filename to load the vertex shader from.
    def loadVertexShader(self, file):
        raise NotImplementedError()

    ##  Load the fragment shader from a file.
    #
    #   \param file \type{string} The filename to load the fragment shader from.
    def loadFragmentShader(self, file):
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
