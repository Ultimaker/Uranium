from UM.Mesh.MeshWriter import MeshWriter
import time
import struct

class OBJWriter(MeshWriter):
    def __init__(self):
        super(OBJWriter, self).__init__()
        self._supported_extension = ".obj"
        
    def write(self, file_name, storage_device, mesh_data):
        if(self._supported_extension in file_name):
            f = storage_device.openFile(file_name, 'wb')
            f.write(("#PLUGGABLE UNICORN OBJ EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S')).ljust(80, '\000'))
            vertices = mesh_data.getVertices()
            for vertex in vertices:
                f.write("v %s %s %s", vertex.getPosition().x,vertex.getPosition().x,vertex.getPosition().x)
            if mesh_data.hasNormals():
                f.write("#Normals ")
                for vertex in vertices:
                    f.write("nv %s %s %s", vertex.getNormal().x,vertex.getNormal().x,vertex.getNormal().x)
            storage_device.closeFile(f)
