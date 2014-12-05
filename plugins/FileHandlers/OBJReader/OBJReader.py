from Cura.MeshHandling.MeshReader import MeshReader
from Cura.MeshHandling.MeshData import MeshData
import os
import struct

class OBJReader(MeshReader):
    def __init__(self):
        super(OBJReader, self).__init__()
        self._supported_extension = ".obj"
        
    def read(self, file_name, storage_device):
        
        mesh = None
        if(self._supported_extension in file_name):
            vertex_list = []
            normal_list = []
            face_list = []

            mesh = MeshData()
            f = storage_device.openFile(file_name, 'rt')
            for line in f:
                parts = line.split()
                if len(parts) < 1:
                    continue
                if parts[0] == 'v': # The data is loaded so that it's axis make more sense
                    vertex_list.append([float(parts[1]), float(parts[2]), float(parts[3])])
                if parts[0] == 'vn':
                    normal_list.append([float(parts[1]), float(parts[2]), float(parts[3])])
                if parts[0] == 'f':
                    parts = [i for i in map(lambda p: p.split('/'), parts)]
                    for idx in range(1, len(parts)-2):
                        data = [int(parts[1][0]), int(parts[idx+1][0]), int(parts[idx+2][0])]
                        if len(parts[1]) > 2:
                            data += [int(parts[1][2]), int(parts[idx+1][2]), int(parts[idx+2][2])]
                        face_list.append(data)
            storage_device.closeFile(f)

            mesh.reserveFaceCount(len(face_list))
            num_vertices = len(vertex_list)
            num_normals = len(normal_list)
            for face in face_list:
                # Substract 1 from index, as obj starts counting at 1 instead of 0
                i = face[0] - 1 
                j = face[1] - 1
                k = face[2] - 1
                #TODO: improve this handling, this can cause weird errors
                if i < 0 or i >= num_vertices:
                    i = 0
                if j < 0 or j >= num_vertices:
                    j = 0
                if k < 0 or k >= num_vertices:
                    k = 0
                if(num_normals == num_vertices):
                    mesh.addFaceWithNormals(vertex_list[i][0], vertex_list[i][1], vertex_list[i][2], normal_list[i][0], normal_list[i][1], normal_list[i][2], vertex_list[j][0], vertex_list[j][1], vertex_list[j][2], normal_list[j][0], normal_list[j][1], normal_list[j][2], vertex_list[k][0], vertex_list[k][1], vertex_list[k][2],normal_list[k][0], normal_list[k][1], normal_list[k][2])
                else:
                    mesh.addFace(vertex_list[i][0], vertex_list[i][1], vertex_list[i][2], vertex_list[j][0], vertex_list[j][1], vertex_list[j][2], vertex_list[k][0], vertex_list[k][1], vertex_list[k][2])
                
            if(num_normals != num_vertices): # We didn't get enough normals for the verts, so calculate them
                volume.calculateNormals()
        return mesh
    
    
