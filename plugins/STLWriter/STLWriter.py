from Cura.MeshHandling.MeshWriter import MeshWriter
import time
import struct

class STLWriter(MeshWriter):
    def __init__(self):
        super(STLWriter, self).__init__()
        self._supported_extention = ".stl"
        
    #TODO: Only a single mesh can be saved to a single file, we might want to save multiple meshes to a single file
    def write(self, file_name, mesh_data):
        print 'WRITING YEAAH' 
        if(self._supported_extention in file_name):
            f = open(file_name, 'wb')
            f.write(("PLUGGABLE UNICORN BINARY STL EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S')).ljust(80, '\000'))
            #print mesh_data.getNumVerts()
            num_verts = mesh_data.getNumVerts()
            f.write(struct.pack("<I", int(num_verts / 3)))
            for index in xrange(0, num_verts, 3):
                #print index
                verts = mesh_data.getVerts()
                v1 = verts[index]
                v2 = verts[index + 1]
                v3 = verts[index + 2]
                f.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                f.write(struct.pack("<fff", v1[0], v1[1], v1[2]))
                f.write(struct.pack("<fff", v2[0], v2[1], v2[2]))
                f.write(struct.pack("<fff", v3[0], v3[1], v3[2]))
                f.write(struct.pack("<H", 0))
            f.close()
            return True
        else:
            return False