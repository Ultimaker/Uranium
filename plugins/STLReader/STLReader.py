from Cura.MeshHandling.MeshReader import MeshReader
from Cura.MeshHandling.MeshData import MeshData
import os

class STLReader(MeshReader):
    def __init__(self):
        super(STLReader, self).__init__()
        self._supported_extension = ".stl"
    
    ## Decide if we need to use ascii or binary in order to read file
    def read(self, file_name):
        mesh = None
        if(self._supported_extension in file_name):
            mesh = MeshData()
            f = open(file_name, "rb")
            if f.read(5).lower() == "solid":
                self._loadAscii(mesh, f)
                if mesh.getNumVerts() < 3:
                    f.seek(5, os.SEEK_SET)
                    self._loadBinary(mesh, f)
            else:
                self._loadBinary(mesh, f)
            f.close()
            mesh.calculateNormals()
        return mesh

    # Private
    ## Load the STL data from file by consdering the data as ascii.
    # \param mesh The MeshData object where the data is written to.
    # \param f The file handle
    def _loadAscii(self, mesh, f):
        num_verts = 0
        for lines in f:
            for line in lines.split('\r'):
                if 'vertex' in line:
                    num_verts += 1
        mesh.reserveVertexCount(num_verts)
        f.seek(5, os.SEEK_SET)
        num_verts = 0
        data = [None,None,None]
        for lines in f:
            for line in lines.split('\r'):
                if 'vertex' in line:
                    data[num_verts] = line.split()[1:]
                    num_verts += 1
                    if num_verts == 3:
                        mesh.addFace(float(data[0][0]), float(data[0][1]), float(data[0][2]), float(data[1][0]), float(data[1][1]), float(data[1][2]), float(data[2][0]), float(data[2][1]), float(data[2][2]))
                        num_verts = 0

    # Private
    ## Load the STL data from file by consdering the data as Binary.
    # \param mesh The MeshData object where the data is written to.
    # \param f The file handle
    def _loadBinary(self, mesh, f):
        f.read(80-5) #Skip the header
        
        num_faces = struct.unpack('<I', f.read(4))[0]
        mesh.reserveFaceCount(num_faces)
        for idx in xrange(0, num_faces):
            data = struct.unpack("<ffffffffffffH", f.read(50))
            mesh.addFace(data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11])