# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
from typing import Any

from UM.FileHandler.FileReader import FileReader
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector


class MeshReader(FileReader):
    def __init__(self, application):
        super().__init__()
        self._application = application

    ##  Read mesh data from file and returns a node that contains the data 
    #   Note that in some cases you can get an entire scene of nodes in this way (eg; 3MF)
    #
    #   \return node \type{SceneNode} or \type{list(SceneNode)} The SceneNode or SceneNodes read from file.
    def read(self, file_name: str, center: bool = True, *args: Any, **kwargs: Any) -> Any:
        results = self._read(file_name)

        if results is not None:
            if not isinstance(results, list):
                results = [results]

            for result in results:
                if center:
                    # If the result has a mesh and no children it needs to be centered
                    if result.getMeshData() and len(result.getChildren()) == 0:
                        extents = result.getMeshData().getExtents()
                        move_vector = Vector(extents.center.x, extents.center.y, extents.center.z)
                        result.setCenterPosition(move_vector)

                    # Move all the meshes of children so that toolhandles are shown in the correct place.
                    for node in result.getChildren():
                        if node.getMeshData():
                            extents = node.getMeshData().getExtents()
                            m = Matrix()
                            m.translate(-extents.center)
                            node.setMeshData(node.getMeshData().getTransformed(m))
                            node.translate(extents.center)

        # read mesh finished
        nodes = results
        for node in nodes:
            node.setSelectable(True)
            node.setName(os.path.basename(file_name))

        mesh_manager = self._application.getMeshManager()
        results = mesh_manager.invoke_mesh_read_finished_callbacks(file_name, results)

        return results

    def _read(self, file_name: str, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("MeshReader plugin was not correctly implemented, no read was specified")
