# Copyright (c) 2016 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.

import struct
import time

from UM.Logger import Logger
from UM.Mesh.MeshWriter import MeshWriter
from UM.i18n import i18nCatalog

catalog = i18nCatalog("uranium")

class STLWriter(MeshWriter):
    def write(self, stream, nodes, mode = MeshWriter.OutputMode.TextMode):
        """Write the specified sequence of nodes to a stream in the STL format.

        :param stream: The output stream to write to.
        :param nodes: A sequence of scene nodes to write to the output stream.
        :param mode: The output mode to use for writing scene nodes. Text mode
        causes the writer to write in STL's ASCII format. Binary mode causes the
        writer to write in STL's binary format. Any other mode is invalid.
        """

        try:
            MeshWriter._meshNodes(nodes).__next__()
        except StopIteration:
            Logger.log("e", "There is no mesh to write.")
            self.setInformation(catalog.i18nc("@error:no mesh", "There is no mesh to write."))
            return False  # Don't try to write a file if there is no mesh.

        if mode == MeshWriter.OutputMode.TextMode:
            self._writeAscii(stream, MeshWriter._meshNodes(nodes))
        elif mode == MeshWriter.OutputMode.BinaryMode:
            self._writeBinary(stream, MeshWriter._meshNodes(nodes))
        else:
            Logger.log("e", "Unsupported output mode writing STL to stream")
            self.setInformation(catalog.i18nc("@error:not supported", "Unsupported output mode writing STL to stream."))
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
                for index in range(0, num_verts - 2, 3):
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
        nodes = list(nodes)
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