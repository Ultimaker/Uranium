from UM.MeshHandling.MeshReader import MeshReader
from UM.MeshHandling.MeshData import MeshData

class PCDReader(MeshReader):
    def __init__(self):
        super(PCDReader, self).__init__()
        self._supported_extension = ".pcd"

    def read(self, file_name, storage_device):
        mesh = None
        if(self._supported_extension in file_name):
            mesh = MeshData()
            header_read = False
            has_normals = False
            f = storage_device.openFile(file_name, 'rt')
            for lines in f:
                for line in lines.split('\r'):
                    if "FIELDS" in line:
                        if "x" in line and "y" in line and "z" in line:
                            if "normal_x" in line and "normal_y" in line and "normal_z" in line:
                                has_normals = True
                        else:
                            return False # Wrong type of PCD file!
                    if "POINTS" in line:
                        mesh.reserveVertexCount(line.split()[1]) # Cuts 'POINTS from line (should leave us with number)
                    if "DATA" in line:
                        if "ascii" not in line:
                            #Can only read ascii
                            return False
                        header_read = True # PCD defines that the final part of the header is the 'data' type. after this, we get points!
                        continue
                    if header_read:
                        vertex_data = line.split()
                        if(has_normals):
                            addVertexWithNormal(vertex_data[0],vertex_data[1],vertex_data[2],vertex_data[3],vertex_data[4],vertex_data[5])
                        else:
                            addVertex(vertex_data[0],vertex_data[1],vertex_data[2])

            storage_device.closeFile(f)

        return mesh
