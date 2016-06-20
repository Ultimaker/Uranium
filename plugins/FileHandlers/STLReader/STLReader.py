# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.MeshReader import MeshReader
from UM.Mesh.MeshData import MeshData
from UM.Logger import Logger
from UM.Scene.SceneNode import SceneNode

import numpy
import stl  # numpy-stl lib
import stl.mesh

# Increase max count. (10 million should be okay-ish)
stl.stl.MAX_COUNT = 10000000

class STLReader(MeshReader):
    def __init__(self):
        super(STLReader, self).__init__()
        self._supported_extensions = [".stl"]

    ## Decide if we need to use ascii or binary in order to read file
    def read(self, file_name):
        mesh_data = None
        scene_node = None

        mesh = MeshData()
        scene_node = SceneNode()

        loaded_data = stl.mesh.Mesh.from_file(file_name)
        vertices = numpy.resize(loaded_data.points.flatten(), (int(loaded_data.points.size / 3), 3))

        # Invert values of second column
        vertices[:,1] *= -1

        # Swap column 1 and 2 (We have a different coordinate system)
        self._swapColumns(vertices, 1, 2)

        mesh.setVertices(vertices)

        # Create an nd array containing indicies of faces.
        # As we have the data duplicated & packed, it will always count up;
        # [[0, 1, 2]
        #  [3, 4, 5]]
        mesh.setIndices(numpy.resize(numpy.arange(int(loaded_data.points.size / 3), dtype=numpy.int32),
                                     (int(loaded_data.points.size / 9), 3)))

        mesh.calculateNormals(fast = True)

        Logger.log("d", "Loaded a mesh with %s vertices", mesh.getVertexCount())
        scene_node.setMeshData(mesh)
        return scene_node

    def _swapColumns(self, array, frm, to):
        array[:, [frm, to]] = array[:, [to, frm]]