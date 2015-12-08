# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

##  Convenience methods for dealing with OpenGL.
#
#   This class simplifies dealing with OpenGL and different implementations
#   of it. It mostly describes an interface that should be implemented for
#   different implementations. Additionally, it provides singleton handling.
#   The implementation-defined subclass should be set as singleton instance
#   as soon as possible.
class OpenGL:
    ##  Different OpenGL chipset vendors.
    class Vendor:
        NVidia = 1
        AMD = 2
        Intel = 3
        Other = 4

    ##  Check if the current OpenGL implementation supports FrameBuffer Objects.
    #
    #   \return True if FBOs are supported, False if not.
    def hasFrameBufferObjects(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Check to see if the current OpenGL implementation has a certain OpenGL extension.
    #
    #   \param extension The extension to query for.
    #
    #   \return True if the extension is available, False if not.
    def hasExtension(self, extension):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Get the current GPU vendor.
    #
    #   \return One of the items of OpenGL.Vendor.
    def getGPUVendor(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Get a string describing the current GPU type.
    #
    #   This effectively should return the OpenGL renderer string.
    def getGPUType(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Get the OpenGL bindings object.
    #
    #   This should return an object that has all supported OpenGL functions
    #   as methods and additionally defines all OpenGL constants. This object
    #   is used to make direct OpenGL calls so should match OpenGL as closely
    #   as possible.
    def getBindingsObject(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Create a FrameBuffer Object.
    #
    #   This should return an implementation-specifc FrameBufferObject subclass.
    def createFrameBufferObject(self, width, height):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Create a Texture Object.
    #
    #   This should return an implementation-specifc Texture subclass.
    def createTexture(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Create a ShaderProgram Object.
    #
    #   This should return an implementation-specifc ShaderProgram subclass.
    def createShaderProgram(self, file_name):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Get the singleton instance.
    #
    #   \return The singleton instance.
    @classmethod
    def getInstance(cls):
        return cls._instance

    ##  Set the singleton instance.
    #
    #   This is mostly meant to simplify the singleton logic and should be called
    #   by the OpenGL implementation as soon as possible.
    @classmethod
    def setInstance(cls, instance):
        cls._instance = instance

    ## private:
    _instance = None
