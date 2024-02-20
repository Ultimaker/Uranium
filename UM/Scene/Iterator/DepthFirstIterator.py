# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from UM.Scene.SceneNode import SceneNode
from . import Iterator


class DepthFirstIterator(Iterator.Iterator):
    def __init__(self, scene_node: SceneNode) -> None:
        super().__init__(scene_node)

    def _fillStack(self) -> None:
        self._addNodesToStack()
        self._setPrintOrderForSliceableNodes()

    def _addNodesToStack(self) -> None:
        self._node_stack.append(self._scene_node)
        self._node_stack.extend(self._scene_node.getAllChildren())

    def _setPrintOrderForSliceableNodes(self) -> None:
        order_counter = 1
        for node in self._node_stack:
            if node.callDecoration("isSliceable"):
                node.printOrder = order_counter
                order_counter += 1
