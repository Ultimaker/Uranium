# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

from UM.Scene.Selection import Selection
from UM.Scene.SceneNode import SceneNode

class AddSceneNodeOperation(Operation.Operation):
    def __init__(self, node, parent):
        super().__init__()
        self._node = node
        self._parent = parent
        self._selected = False

    def undo(self):
        self._node.setParent(None)
        self._selected = Selection.isSelected(self._node)
        if self._selected:
            Selection.remove(self._node)

    def redo(self):
        self._node.setParent(self._parent)
        if self._selected:
            Selection.add(self._node)
