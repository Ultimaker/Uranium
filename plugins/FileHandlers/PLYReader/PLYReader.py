from UM.Mesh.MeshReader import MeshReader
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshData import MeshType
from UM.Logger import Logger
import os
import struct

##      In it's current implementation it reads *only* pointclouds (with or without normals). 
#       It uses the definition as found on http://paulbourke.net/dataformats/ply/

class PLYReader(MeshReader):
    def __init__(self):
        super(PLYReader, self).__init__()
        self._supported_extension = ".ply"
        
    def read(self, file_name, storage_device):
        mesh = None
        
        extension = os.path.splitext(file_name)[1]
        if extension.lower() == self._supported_extension:
            vertex_list = []
            normal_list = []
            face_list = []
            x_location = -1
            y_location = -1
            z_location = -1
            nx_location = -1
            ny_location = -1
            nz_location = -1
            element_location = -1
            read_type = -1
            num_vertices = -1
            mesh = MeshData()
            formatting = b''
            vert_byte_size = 0
            try:
                f = storage_device.openFile(file_name, 'rb')
            except FileNotFoundError:
                Logger.log("w","File %s was not found",file_name)
                return None
            #line_list = list(f) #Put all lines in a list, usefull because we need to read the header first
            
            # Read header
            for index in range(0,250): # It's fairly unlikely that the header will be over 250 lines.
                line = f.readline()
                line = line.decode("utf-8") #We read it as bytes, but the header is made up from strings
                parts = line.split()
                if index == 0:
                    if parts[0] != "ply" and parts[0] != "PLY":
                        Logger.log("e", "The ply file does not adhere to the ply standard. Aborting.")
                        return # First line does not have the magic number. Stop right away!
                if parts[0] == "format":
                    if parts[1] == "ascii":
                        read_type = 0
                    if parts[1] == "binary_little_endian":
                        read_type = 1
                        formatting += b'<'
                        
                    if parts[1] == "binary_big_endian":
                        formatting += b'>'
                
                if parts[0] == "end_header": # End of header, stop reading header (start reading vert data)
                    #start_index = index + 1
                    break
                if parts[0] == "element": 
                    if parts[1] == "vertex": #Found vertex element
                        element_location = index
                        num_vertices = int(parts[2])
                
                if parts[0] == "property": #Check ordering 
                    if parts[2] == "x":
                        x_location = index - element_location - 1
                    if parts[2] == "y":
                        y_location = index - element_location - 1
                    if parts[2] == "z":
                        z_location = index - element_location - 1
                    if parts[2] == "nx":
                        nx_location = index - element_location - 1
                    if parts[2] == "ny":
                        ny_location = index - element_location - 1
                    if parts[2] == "nz":
                        nz_location = index - element_location - 1
                        
                    if parts[1] == 'float': #check type!
                        formatting += b'f'
                        vert_byte_size += 4
                        
            
            has_normals = (nx_location != -1 and ny_location != -1 and nz_location != -1)
            
            # Read vert data
            if read_type == 0: # ASCII
                for index, line in enumerate(f.readlines()):
                    if index > num_vertices: #The ply can have edges, but we ignore them as we interpret it as a point cloud
                        break
                    line = line.decode("utf-8") # This is ascii type, not bytes
                    parts = line.split()
                    if has_normals: 
                        mesh.addVertexWithNormal(parts[x_location],parts[y_location],parts[z_location],parts[nx_location],parts[ny_location],parts[nz_location])
                    else:
                        mesh.addVertex(parts[x_location],parts[y_location],parts[z_location])
            else: #binary
                for index in range(0, num_vertices):
                    data = struct.unpack(formatting, f.read(vert_byte_size))
                    if has_normals:
                        mesh.addVertexWithNormal(data[x_location],data[y_location],data[z_location],data[nx_location],data[ny_location],data[nz_location])
                    else: 
                        mesh.addVertex(data[x_location],data[y_location],data[z_location])
                
            Logger.log("d", "Loaded a mesh with %s vertices", mesh.getVertexCount())
            mesh.setType(MeshType.pointcloud) #PLY reading defaults to pointcloud at the moment
            return mesh