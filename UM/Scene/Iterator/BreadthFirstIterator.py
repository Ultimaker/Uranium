# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import Iterator
from UM.Scene.SceneNode import SceneNode


class BreadthFirstIterator(Iterator.Iterator):
    def __init__(self, scene_node: SceneNode) -> None:
        super().__init__(scene_node)

    def _fillStack(self) -> None:
        self._node_stack.append(self._scene_node)
        for node in self._node_stack:  # Loop through list, add children to back of list
            self._node_stack.extend(node.getChildren())