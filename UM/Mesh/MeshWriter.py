# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.FileHandler.FileWriter import FileWriter
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.SceneNode import SceneNode


##  Base class for mesh writer objects
class MeshWriter(FileWriter):
    def __init__(self):
        super().__init__()
    
    ##  Output a collection of nodes to stream in such a way that it makes sense
    #   for the file format.
    #
    #   For example, in case of STL, it makes sense to go through all children
    #   of the nodes and write all those as transformed vertices to a single
    #   file.
    #
    #   \param stream \type{IOStream} The stream to output to.
    #   \param nodes A collection of scene nodes to write to the stream.
    def write(self, stream, node):
        raise NotImplementedError("MeshWriter plugin was not correctly implemented, no write was specified")

    ##  Filters a collection of nodes to only include nodes that are actual
    #   meshes.
    #
    #   This does not include auxiliary nodes such as tool handles.
    #
    #   \param nodes A sequence of nodes.
    #   \return The nodes among those that are actual scene nodes.
    @staticmethod
    def _meshNodes(nodes):
        for root in nodes:
            yield from filter(
                lambda child: type(child) is SceneNode and child.getMeshData(),
                BreadthFirstIterator(root)
            )