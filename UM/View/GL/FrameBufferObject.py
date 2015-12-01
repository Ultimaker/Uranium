# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

class FrameBufferObject:
    def __init__(self):
        pass

    def getTextureId(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    def bind(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    def release(self):
        raise NotImplementedError("Should be reimplemented by subclasses")

    def getContents(self):
        raise NotImplementedError("Should be reimplemented by subclasses")
