from UM.Mesh.MeshWriter import MeshWriter
import time
import struct

class STLWriter(MeshWriter):
    def __init__(self):
        super(STLWriter, self).__init__()
        self._supported_extension = ".stl"
        
    #TODO: Only a single mesh can be saved to a single file, we might want to save multiple meshes to a single file
    ##  Write the Mesh to file.
    #   \param file_name Location to write to
    #   \param storage_device Device to write to.
    #   \param mesh_data MeshData to write.
    def write(self, file_name, storage_device, mesh_data):
        if(self._supported_extension in file_name):
            f = storage_device.openFile(file_name, 'wb')
            f.write(bytes("PLUGGABLE UNICORN BINARY STL EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S'),"utf-8"))
            num_verts = mesh_data.getVertexCount()
            f.write(struct.pack("<I", int(num_verts / 3))) #Write number of faces to STL
            verts = mesh_data.getVertices()
            for index in range(0, num_verts-1, 3):
                v1 = verts[index]
                v2 = verts[index + 1]
                v3 = verts[index + 2]
                f.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                f.write(struct.pack("<fff", v1[0], v1[1], v1[2]))
                f.write(struct.pack("<fff", v2[0], v2[1], v2[2]))
                f.write(struct.pack("<fff", v3[0], v3[1], v3[2]))
                f.write(struct.pack("<H", 0))
            storage_device.closeFile(f)
            return True
        else:
            return False
