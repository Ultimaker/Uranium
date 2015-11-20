# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

class OpenGL:
    def isAvailable(self):
        return False

    def hasFrameBufferObjects(self):
        return False

    def hasExtension(self, extension):
        return False

    def getGPUVendor(self):
        return None

    def getGPUType(self):
        return None

    @classmethod
    def getInstance(cls):
        return cls._instance

    _instance = None