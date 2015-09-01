# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from UM.Application import Application

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

        # Hack to ensure that the _onchanged is triggered correctly.
        # We can't do it the right way as most remove changes don't need to trigger
        # a reslice (eg; removing hull nodes don't need to trigger reslice).
        Application.getInstance().getBackend().forceSlice()
        if Selection.isSelected(self._node):
            Selection.remove(self._node)
