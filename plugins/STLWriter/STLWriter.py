from Cura.MeshHandling.MeshWriter import MeshWriter
import time
import struct

class STLWriter(MeshWriter):
    def __init__(self):
        super(STLWriter, self).__init__()
        self._supported_extension = ".stl"
        
    #TODO: Only a single mesh can be saved to a single file, we might want to save multiple meshes to a single file
    def write(self, file_name, storage_device, mesh_data):
        if(self._supported_extension in file_name):
            f = storage_device.openFile(file_name, 'wb')
            f.write(("PLUGGABLE UNICORN BINARY STL EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S')).ljust(80, '\000'))
            num_verts = mesh_data.getNumVerts()
            f.write(struct.pack("<I", int(num_verts / 3))) #Write number of faces to STL
            for index in xrange(0, num_verts, 3):
                verts = mesh_data.getVerts()
                v1 = verts[index]
                v2 = verts[index + 1]
                v3 = verts[index + 2]
                f.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                vertPos = v1.getPosition()
                f.write(struct.pack("<fff", vertPos.x, vertPos.y, vertPos.z))
                vertPos = v2.getPosition()
                f.write(struct.pack("<fff", vertPos.x, vertPos.y, vertPos.z))
                vertPos = v3.getPosition()
                f.write(struct.pack("<fff", vertPos.x, vertPos.y, vertPos.z))
                f.write(struct.pack("<H", 0))
            f.close()
            return True
        else:
            return False
