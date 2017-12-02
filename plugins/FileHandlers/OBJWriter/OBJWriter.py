# Copyright (c) 2016 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Mesh.MeshWriter import MeshWriter
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.SceneNode import SceneNode

import time
import struct

class OBJWriter(MeshWriter):
    ##  Writes the specified nodes to a stream in the OBJ format.
    #
    #   \param stream The stream to write the OBJ data to.
    #   \param nodes The nodes to write as OBJ data.
    #   \param mode Additional information on how to serialise the OBJ format.
    #   The OBJ format only supports text mode.
    def write(self, stream, nodes, mode = MeshWriter.OutputMode.TextMode):
        if mode != MeshWriter.OutputMode.TextMode:
            return False

        try:
            MeshWriter._meshNodes(nodes).__next__()
        except StopIteration:
            return False #Don't write files without mesh data.

        stream.write("# URANIUM OBJ EXPORT {0}\n".format(time.strftime("%a %d %b %Y %H:%M:%S")))

        face_offset = 1
        for node in MeshWriter._meshNodes(nodes):
            mesh_data = node.getMeshData().getTransformed(node.getWorldTransformation())
            verts = mesh_data.getVertices()
            if verts is None:
                continue   # No mesh data, nothing to do.

            stream.write("# {0}\n# Vertices\n".format(node.getName()))

            if mesh_data.hasIndices():
                for face in mesh_data.getIndices():
                    v1 = verts[face[0]]
                    v2 = verts[face[1]]
                    v3 = verts[face[2]]
                    stream.write("v {0} {1} {2}\n".format(v1[0], -v1[2], v1[1]))
                    stream.write("v {0} {1} {2}\n".format(v2[0], -v2[2], v2[1]))
                    stream.write("v {0} {1} {2}\n".format(v3[0], -v3[2], v3[1]))

                stream.write("# Faces\n")
                for face in mesh_data.getIndices():
                    stream.write("f {0} {1} {2}\n".format(face[0] + face_offset, face[1] + face_offset, face[2] + face_offset))
            else:
                for vertex in verts:
                    stream.write("v {0} {1} {2}\n".format(vertex[0], -vertex[2], vertex[1]))

                stream.write("# Faces\n")
                for face in range(face_offset, face_offset + len(verts) - 1, 3):
                    stream.write("f {0} {1} {2}\n".format(face, face + 1, face + 2))

            face_offset += mesh_data.getVertexCount()

        return True
