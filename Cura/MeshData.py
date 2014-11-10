# Class to hold a list of verts and possibly how (and if) they are connected.
class MeshData(object):
    __init__(self):
        self._verts = []
        
    def getVerts(self):
        return self._verts