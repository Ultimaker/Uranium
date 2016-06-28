# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.MeshReader import MeshReader
from UM.Mesh.MeshBuilder import MeshBuilder
import os
from UM.Scene.SceneNode import SceneNode

from UM.Job import Job

class OBJReader(MeshReader):
    def __init__(self):
        super(OBJReader, self).__init__()
        self._supported_extensions = [".obj"]

    def read(self, file_name):
        scene_node = None

        extension = os.path.splitext(file_name)[1]
        if extension.lower() in self._supported_extensions:
            vertex_list = []
            normal_list = []
            uv_list = []
            face_list = []
            scene_node = SceneNode()

            mesh_builder = MeshBuilder()
            mesh_builder.setFileName(file_name)
            f = open(file_name, "rt")
            for line in f:
                parts = line.split()
                if len(parts) < 1:
                    continue
                if parts[0] == "v":
                    vertex_list.append([float(parts[1]), float(parts[3]), -float(parts[2])])
                if parts[0] == "vn":
                    normal_list.append([float(parts[1]), float(parts[3]), -float(parts[2])])
                if parts[0] == "vt":
                    uv_list.append([float(parts[1]), float(parts[2])])
                if parts[0] == "f":
                    parts = [i for i in map(lambda p: p.split("/"), parts)]
                    for idx in range(1, len(parts)-2):
                        data = [int(parts[1][0]), int(parts[idx+1][0]), int(parts[idx+2][0])]
                        if len(parts[1]) > 2:
                            data += [int(parts[1][2]), int(parts[idx+1][2]), int(parts[idx+2][2])]

                            if parts[1][1] and parts[idx+1][1] and parts[idx+2][1]:
                                data += [int(parts[1][1]), int(parts[idx+1][1]), int(parts[idx+2][1])]
                        face_list.append(data)
                Job.yieldThread()
            f.close()

            mesh_builder.reserveVertexCount(3 * len(face_list))
            num_vertices = len(vertex_list)
            num_normals = len(normal_list)

            for face in face_list:
                # Substract 1 from index, as obj starts counting at 1 instead of 0
                i = face[0] - 1
                j = face[1] - 1
                k = face[2] - 1

                if len(face) > 3:
                    ni = face[3] - 1
                    nj = face[4] - 1
                    nk = face[5] - 1
                else:
                    ni = -1
                    nj = -1
                    nk = -1

                if len(face) > 6:
                    ui = face[6] - 1
                    uj = face[7] - 1
                    uk = face[8] - 1
                else:
                    ui = -1
                    uj = -1
                    uk = -1

                #TODO: improve this handling, this can cause weird errors (negative indexes are relative indexes, and are not properly handled)
                if i < 0 or i >= num_vertices:
                    i = 0
                if j < 0 or j >= num_vertices:
                    j = 0
                if k < 0 or k >= num_vertices:
                    k = 0
                if ni != -1 and nj != -1 and nk != -1:
                    mesh_builder.addFaceWithNormals(vertex_list[i][0], vertex_list[i][1], vertex_list[i][2], normal_list[ni][0], normal_list[ni][1], normal_list[ni][2], vertex_list[j][0], vertex_list[j][1], vertex_list[j][2], normal_list[nj][0], normal_list[nj][1], normal_list[nj][2], vertex_list[k][0], vertex_list[k][1], vertex_list[k][2],normal_list[nk][0], normal_list[nk][1], normal_list[nk][2])
                else:
                    mesh_builder.addFaceByPoints(vertex_list[i][0], vertex_list[i][1], vertex_list[i][2], vertex_list[j][0], vertex_list[j][1], vertex_list[j][2], vertex_list[k][0], vertex_list[k][1], vertex_list[k][2])

                if ui != -1:
                    mesh_builder.setVertexUVCoordinates(mesh_builder.getVertexCount() - 3, uv_list[ui][0], uv_list[ui][1])

                if uj != -1:
                    mesh_builder.setVertexUVCoordinates(mesh_builder.getVertexCount() - 2, uv_list[uj][0], uv_list[uj][1])

                if uk != -1:
                    mesh_builder.setVertexUVCoordinates(mesh_builder.getVertexCount() - 1, uv_list[uk][0], uv_list[uk][1])

                Job.yieldThread()
            if not mesh_builder.hasNormals():
                mesh_builder.calculateNormals(fast = True)
            scene_node.setMeshData(mesh_builder.build())

        return scene_node
