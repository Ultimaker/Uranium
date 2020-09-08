# Copyright (c) 2020 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.

import os

from UM.Job import Job
from UM.Logger import Logger
from UM.Mesh.MeshReader import MeshReader
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Scene.SceneNode import SceneNode


class OBJReader(MeshReader):
    def __init__(self) -> None:
        super().__init__()
        self._supported_extensions = [".obj"]

    def _toAbsoluteIndex(self, max, data):
        """ Handle negative indices (those are relative to the position, so -2 is the second one before the face). """
        return [index if index > 0 else 1 + max + index for index in data]

    def _read(self, file_name):
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
            previous_line_parts = []
            f = open(file_name, "rt", encoding = "utf-8")
            for line in f:
                parts = previous_line_parts + line.split()
                previous_line_parts = []
                if len(parts) < 1:
                    continue
                if parts[-1] == "\\":
                    del parts[-1]
                    previous_line_parts = parts
                    continue
                if parts[0] == "f":
                    parts = [i for i in map(lambda p: p.split("/"), parts)]
                    for idx in range(1, len(parts) - 2):
                        data = self._toAbsoluteIndex(len(vertex_list), [int(parts[1][0]), int(parts[idx + 1][0]), int(parts[idx + 2][0])])
                        if len(parts[1]) > 1:
                            if parts[1][1] and parts[idx + 1][1] and parts[idx + 2][1]:
                                data += self._toAbsoluteIndex(len(normal_list), [int(parts[1][1]), int(parts[idx + 1][1]), int(parts[idx + 2][1])])

                            if len(parts[1]) > 2:
                                data += self._toAbsoluteIndex(len(uv_list), [int(parts[1][2]), int(parts[idx + 1][2]), int(parts[idx + 2][2])])
                        face_list.append(data)
                elif parts[0] == "v":
                    vertex_list.append([float(parts[1]), float(parts[3]), -float(parts[2])])
                elif parts[0] == "vn":
                    normal_list.append([float(parts[1]), float(parts[3]), -float(parts[2])])
                elif parts[0] == "vt":
                    uv_list.append([float(parts[1]), float(parts[2])])
                Job.yieldThread()
            f.close()

            mesh_builder.reserveVertexCount(3 * len(face_list))
            num_vertices = len(vertex_list)

            for face in face_list:
                # Substract 1 from index, as obj starts counting at 1 instead of 0
                i = face[0] - 1
                j = face[1] - 1
                k = face[2] - 1

                if len(face) > 3:
                    ui = face[3] - 1
                    uj = face[4] - 1
                    uk = face[5] - 1
                else:
                    ui = -1
                    uj = -1
                    uk = -1

                if len(face) > 6:
                    ni = face[6] - 1
                    nj = face[7] - 1
                    nk = face[8] - 1
                else:
                    ni = -1
                    nj = -1
                    nk = -1

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

                if ui != -1 and len(uv_list) > ui:
                    mesh_builder.setVertexUVCoordinates(mesh_builder.getVertexCount() - 3, uv_list[ui][0], uv_list[ui][1])

                if uj != -1 and len(uv_list) > uj:
                    mesh_builder.setVertexUVCoordinates(mesh_builder.getVertexCount() - 2, uv_list[uj][0], uv_list[uj][1])

                if uk != -1 and len(uv_list) > uk:
                    mesh_builder.setVertexUVCoordinates(mesh_builder.getVertexCount() - 1, uv_list[uk][0], uv_list[uk][1])

                Job.yieldThread()
            if not mesh_builder.hasNormals():
                mesh_builder.calculateNormals(fast = True)

            # make sure that the mesh data is not empty
            if mesh_builder.getVertexCount() == 0:
                Logger.log("d", "File did not contain valid data, unable to read.")
                return None  # We didn't load anything.

            scene_node.setMeshData(mesh_builder.build())

        return scene_node
