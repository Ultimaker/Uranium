# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

class OpenGL:
    class Vendor:
        NVidia = 1
        AMD = 2
        Intel = 3
        Other = 4

    def hasFrameBufferObjects(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def hasExtension(self, extension):
        raise NotImplementedError("Should be implemented by subclasses")

    def getGPUVendor(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def getGPUType(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def getBindingsObject(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def createFrameBufferObject(self, width, height):
        raise NotImplementedError("Should be implemented by subclasses")

    def createTexture(self, width, height):
        raise NotImplementedError("Should be implemented by subclasses")

    def createMaterial(self, file_name):
        raise NotImplementedError("Should be implemented by subclasses")

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            raise ValueError("No OpenGL instance created!")

        return cls._instance

    @classmethod
    def setInstance(cls, instance):
        cls._instance = instance

    _instance = None
