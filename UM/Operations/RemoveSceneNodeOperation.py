# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from UM.Scene.SceneNode import SceneNode
from . import Operation

from UM.Scene.Selection import Selection
from UM.Application import Application


class RemoveSceneNodeOperation(Operation.Operation):
    """An operation that removes a SceneNode from the scene."""

    def __init__(self, node: SceneNode) -> None:
        """Initialises the RemoveSceneNodeOperation.

        :param node: The node to remove.
        """

        super().__init__()
        self._node = node
        self._parent = node.getParent()

    def undo(self) -> None:
        """Undoes the operation, putting the node back in the scene."""

        self._node.setParent(self._parent)  # Hanging it back under its original parent puts it back in the scene.

    def redo(self) -> None:
        """Redo the operation, removing the node again."""

        old_parent = self._parent
        self._node.setParent(None)

        if old_parent and old_parent.callDecoration("isGroup"):
            old_parent.callDecoration("recomputeConvexHull")

        # Hack to ensure that the _onchanged is triggered correctly.
        # We can't do it the right way as most remove changes don't need to trigger
        # a reslice (eg; removing hull nodes don't need to trigger a reslice).
        try:
            Application.getInstance().getBackend().needsSlicing()  # type: ignore
        except AttributeError:  # Todo: This should be removed, Uranium doesn't care or know about slicing!
            pass
        if Selection.isSelected(self._node):  # Also remove the selection.
            Selection.remove(self._node)
