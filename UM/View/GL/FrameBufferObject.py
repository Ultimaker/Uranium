# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

##  An interface for OpenGL FrameBuffer Objects.
#
#   This class describes a minimal interface that is expected of FrameBuffer Object
#   classes.
class FrameBufferObject:
    def __init__(self):
        pass

    ##  Get the texture ID of the texture target of this FBO.
    def getTextureId(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Bind the FBO so it can be rendered to.
    def bind(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Release the FBO so it will no longer be rendered to.
    def release(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    ##  Get the contents of the FBO as an image data object.
    def getContents(self):
        raise NotImplementedError("Should be reimplemented by subclasses")
