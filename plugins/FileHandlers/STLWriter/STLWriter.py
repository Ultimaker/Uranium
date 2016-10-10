# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.MeshWriter import MeshWriter
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Logger import Logger

import time
import struct
import os

class STLWriter(MeshWriter):
    ##  Write the Mesh to file.
    #   \param file_name Location to write to
    #   \param storage_device Device to write to.
    #   \param mesh_data MeshData to write.
    def write(self, stream, node, mode = MeshWriter.OutputMode.TextMode):
        nodes = []
        for n in BreadthFirstIterator(node):
            if type(n) is not SceneNode or not n.getMeshData():
                continue

            nodes.append(n)

        if not nodes:
            return False

        if mode == MeshWriter.OutputMode.TextMode:
            self._writeAscii(stream, nodes)
        elif mode == MeshWriter.OutputMode.BinaryMode:
            self._writeBinary(stream, nodes)
        else:
            Logger.log("e", "Unsupported output mode writing STL to stream")
            return False

        return True

    def _writeAscii(self, stream, nodes):
        name = "Uranium STLWriter {0}".format(time.strftime("%a %d %b %Y %H:%M:%S"))
        stream.write("solid {0}\n".format(name))

        for node in nodes:
            mesh_data = node.getMeshData().getTransformed(node.getWorldTransformation())
            verts = mesh_data.getVertices()
            if verts is None:
                continue  # No mesh data, nothing to do.

            if mesh_data.hasIndices():
                for face in mesh_data.getIndices():
                    stream.write("facet normal 0.0 0.0 0.0\n")
                    stream.write("  outer loop\n")

                    v1 = verts[face[0]]
                    v2 = verts[face[1]]
                    v3 = verts[face[2]]
                    stream.write("    vertex {0} {1} {2}\n".format(v1[0], -v1[2], v1[1]))
                    stream.write("    vertex {0} {1} {2}\n".format(v2[0], -v2[2], v2[1]))
                    stream.write("    vertex {0} {1} {2}\n".format(v3[0], -v3[2], v3[1]))

                    stream.write("  endloop\n")
                    stream.write("endfacet\n")
            else:
                num_verts = mesh_data.getVertexCount()
                for index in range(0, num_verts - 1, 3):
                    stream.write("facet normal 0.0 0.0 0.0\n")
                    stream.write("  outer loop\n")
                    v1 = verts[index]
                    v2 = verts[index + 1]
                    v3 = verts[index + 2]
                    stream.write("    vertex {0} {1} {2}\n".format(v1[0], -v1[2], v1[1]))
                    stream.write("    vertex {0} {1} {2}\n".format(v2[0], -v2[2], v2[1]))
                    stream.write("    vertex {0} {1} {2}\n".format(v3[0], -v3[2], v3[1]))

                    stream.write("  endloop\n")
                    stream.write("endfacet\n")

        stream.write("endsolid {0}\n".format(name))

    def _writeBinary(self, stream, nodes):
        stream.write("Uranium STLWriter {0}".format(time.strftime("%a %d %b %Y %H:%M:%S")).encode().ljust(80, b"\000"))

        face_count = 0
        for node in nodes:
            if node.getMeshData().hasIndices():
                face_count += node.getMeshData().getFaceCount()
            else:
                face_count += node.getMeshData().getVertexCount() / 3

        stream.write(struct.pack("<I", int(face_count))) #Write number of faces to STL

        for node in nodes:
            mesh_data = node.getMeshData().getTransformed(node.getWorldTransformation())

            if mesh_data.hasIndices():
                verts = mesh_data.getVertices()
                for face in mesh_data.getIndices():
                    v1 = verts[face[0]]
                    v2 = verts[face[1]]
                    v3 = verts[face[2]]
                    stream.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                    stream.write(struct.pack("<fff", v1[0], -v1[2], v1[1]))
                    stream.write(struct.pack("<fff", v2[0], -v2[2], v2[1]))
                    stream.write(struct.pack("<fff", v3[0], -v3[2], v3[1]))
                    stream.write(struct.pack("<H", 0))
            else:
                num_verts = mesh_data.getVertexCount()
                verts = mesh_data.getVertices()
                for index in range(0, num_verts - 1, 3):
                    v1 = verts[index]
                    v2 = verts[index + 1]
                    v3 = verts[index + 2]
                    stream.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                    stream.write(struct.pack("<fff", v1[0], -v1[2], v1[1]))
                    stream.write(struct.pack("<fff", v2[0], -v2[2], v2[1]))
                    stream.write(struct.pack("<fff", v3[0], -v3[2], v3[1]))
                    stream.write(struct.pack("<H", 0))