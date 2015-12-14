# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

##  A class describing the interface to be used for texture objects.
#
#   This interface should be implemented by OpenGL implementations to handle texture
#   objects.
class Texture:
    def __init__(self):
        pass

    ##  Get the OpenGL ID of the texture.
    def getTextureId(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Bind the texture to a certain texture unit.
    #
    #   \param texture_unit The texture unit to bind to.
    def bind(self, texture_unit = 0):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Release the texture from a certain texture unit.
    #
    #   \param texture_unit The texture unit to release from.
    def release(self, texture_unit = 0):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Load an image and upload it to the texture.
    #
    #   \param file_name The file name of the image to load.
    def load(self, file_name):
        raise NotImplementedError("Should be implemented by subclasses")
