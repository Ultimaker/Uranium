import numpy
# Class to hold a list of verts and possibly how (and if) they are connected.
class MeshData(object):
    def __init__(self):
        self._verts = None
        
        
    def getVerts(self):
        return self._verts