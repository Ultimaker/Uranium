# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

class Texture:
    def __init__(self):
        pass

    def getTextureId(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def bind(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def release(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def setData(self, data):
        raise NotImplementedError("Should be implemented by subclasses")

    def getData(self):
        raise NotImplementedError("Should be implemented by subclasses")
