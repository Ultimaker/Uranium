# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.FileHandler.FileWriter import FileWriter
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.SceneNode import SceneNode


class MeshWriter(FileWriter):
    """Base class for mesh writer objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write(self, stream, node, mode = FileWriter.OutputMode.BinaryMode):
        """Output a collection of nodes to stream in such a way that it makes sense
        for the file format.

        For example, in case of STL, it makes sense to go through all children
        of the nodes and write all those as transformed vertices to a single
        file.

        :param stream: :type{IOStream} The stream to output to.
        :param node: A collection of scene nodes to write to the stream.
        """

        raise NotImplementedError("MeshWriter plugin was not correctly implemented, no write was specified")

    @staticmethod
    def _meshNodes(nodes):
        """Filters a collection of nodes to only include nodes that are actual
        meshes.

        This does not include auxiliary nodes such as tool handles.

        :param nodes: A sequence of nodes.
        :return: The nodes among those that are actual scene nodes.
        """

        for root in nodes:
            yield from filter(
                lambda child: isinstance(child, SceneNode) and child.isSelectable() and child.getMeshData(),
                BreadthFirstIterator(root)
            )