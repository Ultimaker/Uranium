# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection

##  An operation that removes an list of SceneNode from the scene.
class RemoveSceneNodeOperation(Operation.Operation):
    def __init__(self, node):
        super().__init__()
        self._node = node
        self._parent = node.getParent()

    def undo(self):
        self._node.setParent(self._parent)

    def redo(self):
        self._node.setParent(None)
        if Selection.isSelected(self._node):
            Selection.remove(self._node)
