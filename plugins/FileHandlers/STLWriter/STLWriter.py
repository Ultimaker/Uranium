from UM.Mesh.MeshWriter import MeshWriter
import time
import struct
import os

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
        extension = os.path.splitext(file_name)[1]
        if extension.lower() == self._supported_extension and mesh_data is not None and storage_device is not None:
            f = storage_device.openFile(file_name, 'wb')
            f.write(bytes(("Uranium STLWriter " + time.strftime('%a %d %b %Y %H:%M:%S')).ljust(80, '\000'),"utf-8"))
            if mesh_data.getIndices() is not None:
                num_faces = len(mesh_data.getIndices())
                f.write(struct.pack("<I", int(num_faces))) #Write number of faces to STL
                verts = mesh_data.getVertices()
                for face in mesh_data.getIndices():
                    v1 = verts[face[0]]
                    v2 = verts[face[1]]
                    v3 = verts[face[2]]
                    f.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                    f.write(struct.pack("<fff", v1[0], v1[1], v1[2]))
                    f.write(struct.pack("<fff", v2[0], v2[1], v2[2]))
                    f.write(struct.pack("<fff", v3[0], v3[1], v3[2]))
                    f.write(struct.pack("<H", 0))
                '''for index in range(0, num_indices-1, 1):
                    v1 = verts[index]
                    v2 = verts[index + 1]
                    v3 = verts[index + 2]
                    f.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                    f.write(struct.pack("<fff", v1[0], v1[1], v1[2]))
                    f.write(struct.pack("<fff", v2[0], v2[1], v2[2]))
                    f.write(struct.pack("<fff", v3[0], v3[1], v3[2]))
                    f.write(struct.pack("<H", 0))'''
                storage_device.closeFile(f)
                return True
        else:
            return False
