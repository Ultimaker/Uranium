from UM.Mesh.MeshReader import MeshReader
from UM.Mesh.MeshData import MeshData
from UM.Logger import Logger
import os
import struct

# In it's current implementation it reads *only* pointclouds (with or without normals). 

class PLYReader(MeshReader):
    def __init__(self):
        super(PLYReader, self).__init__()
        self._supported_extension = ".ply"
        
    def read(self, file_name, storage_device):
        mesh = None
        
        if(self._supported_extension in file_name):
            vertex_list = []
            normal_list = []
            face_list = []
            x_location = -1
            y_location = -1
            z_location = -1
            nx_location = -1
            ny_location = -1
            nz_location = -1
            start_index = -1
            element_location = -1
            mesh = MeshData()
            f = storage_device.openFile(file_name, 'rt')
            line_list = list(f) #Put all lines in a list, usefull because we need to read the header first
            
            # Read header
            for index, line in enumerate(line_list):
                parts = line.split()
                if index == 0:
                    print(parts)
                    print(parts[0])
                    if parts[0] != "ply" and parts[0] != "PLY":
                        Logger.log("e", "The ply file does not adhere to the ply standard. Aborting.")
                        return # First line does not have the magic number. Stop right away!
                
                if parts[0] == "end_header": # End of header, stop reading header (start reading vert data)
                    start_index = index + 1
                    break
                if parts[0] == "element" and parts[1] == "vertex": #Found vertex element
                    element_location = index
                
                if parts[0] == "property" and parts[1] == 'float': #The order of these elements decides what the data of the verts means
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
            
            has_normals = (nx_location != -1 and ny_location != -1 and nz_location != -1) 
            
            # Read vert data
            for line in line_list[start_index:-1]:  # Go over all data after header data (-1 indicates end of list)
                parts = line.split()
                if has_normals: 
                    mesh.addVertexWithNormal(parts[x_location],parts[y_location],parts[z_location],parts[nx_location],parts[ny_location],parts[nz_location])
                else:
                    mesh.addVertex(parts[x_location],parts[y_location],parts[z_location])
            Logger.log("d", "Loaded a mesh with %s vertices", mesh.getVertexCount())
            return mesh