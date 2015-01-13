from UM.Mesh.MeshWriter import MeshWriter
import time
import struct

class PLYWriter(MeshWriter):
    def __init__(self):
        super(PLYWriter, self).__init__()
        self._supported_extension = ".ply"
        
    def write(self, file_name, storage_device, mesh_data):
        if(self._supported_extension in file_name):
            f = storage_device.openFile(file_name, 'wb')
            num_verts = mesh_data.getVertexCount() - 1
            #bytes("PLUGGABLE UNICORN BINARY STL EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S') + "\n","utf-8")
            f.write(bytes("ply \n","utf-8")) #Magic number that the file needs to start with
            f.write(bytes("format ascii 1.0\n","utf-8")) #Can also be: format binary_little_endian 1.0 or format binary_big_endian 1.0 (for binary)
            f.write(bytes("comment URANIUM ply writer created at " + time.strftime('%a %d %b %Y %H:%M:%S') + "\n","utf-8"))
            
            f.write(bytes("element vertex " + str(num_verts) + "\n", "utf-8")) 
            f.write(bytes("property float x\n", "utf-8")) # Tell the ply that there is a property called x for vertex.
            f.write(bytes("property float y\n", "utf-8")) # Tell the ply that there is a property called y for vertex.
            f.write(bytes("property float z\n", "utf-8")) # Tell the ply that there is a property called z for vertex.
            f.write(bytes("property float Nx\n", "utf-8")) # Tell the ply that there is a property called n_x for vertex (normal).
            f.write(bytes("property float Ny\n", "utf-8")) # Tell the ply that there is a property called n_x for vertex (normal).
            f.write(bytes("property float Nz\n", "utf-8")) # Tell the ply that there is a property called n_x for vertex (normal).
            f.write(bytes("end_header\n", "utf-8")) #Notify end of header  (and start of verts)
            
            positions = mesh_data.getVertices()
            normals = mesh_data.getNormals()
            for index in range(0, num_verts):
                data = "" + str(positions[index][0]) + " " + str(positions[index][1]) + " " + str(positions[index][2])
                data += " " + str(normals[index][0]) + " " + str(normals[index][1]) + " " + str(normals[index][2])
                data += "\n"
                f.write(bytes(data, "utf-8"))

            #vertices = mesh_data.getVertices()
            
            storage_device.closeFile(f)
