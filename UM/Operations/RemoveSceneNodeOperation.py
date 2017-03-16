# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

from UM.Scene.Selection import Selection
from UM.Application import Application


##  An operation that removes a SceneNode from the scene.
class RemoveSceneNodeOperation(Operation.Operation):
    ##  Initialises the RemoveSceneNodeOperation.
    #
    #   \param node The node to remove.
    def __init__(self, node):
        super().__init__()
        self._node = node
        self._parent = node.getParent()

    ##  Undoes the operation, putting the node back in the scene.
    def undo(self):
        self._node.setParent(self._parent)  # Hanging it back under its original parent puts it back in the scene.

    ##  Redo the operation, removing the node again.
    def redo(self):
        old_parent = self._parent
        self._node.setParent(None)

        if old_parent and old_parent.callDecoration("isGroup"):
            old_parent.callDecoration("recomputeConvexHull")

        # Hack to ensure that the _onchanged is triggered correctly.
        # We can't do it the right way as most remove changes don't need to trigger
        # a reslice (eg; removing hull nodes don't need to trigger reslice).
        try:
            Application.getInstance().getBackend().needsSlicing()
        except:
            pass
        if Selection.isSelected(self._node):  # Also remove the selection.
            Selection.remove(self._node)
