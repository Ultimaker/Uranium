# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from UM.Scene.SceneNode import SceneNode

from typing import List, Iterable

##    Abstract iterator class.
class Iterator:
    def __init__(self, scene_node: SceneNode) -> None:
        super().__init__() # Call super to make multiple inheritance work.
        self._scene_node = scene_node
        self._node_stack = []  # type: List[SceneNode]
        self._fillStack()
    
    ##   Fills the list of nodes by a certain order. The strategy to do this is to be defined by the child.
    def _fillStack(self) -> None:
        raise NotImplementedError("Iterator is not correctly implemented. Requires a _fill_stack implementation.")
    
    def __iter__(self) -> Iterable[SceneNode]:
        return iter(self._node_stack)