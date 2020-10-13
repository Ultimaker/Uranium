# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Operations.Operation import Operation

from UM.Scene.Selection import Selection

from UM.Scene.SceneNode import SceneNode

from typing import Optional


class AddSceneNodeOperation(Operation):
    """Operation that adds a new node to the scene."""

    def __init__(self, node: SceneNode, parent: Optional[SceneNode]) -> None:
        """Creates the scene node operation.

        This saves the node and its parent to be able to search for the node to
        remove the node if we want to undo, and to be able to re-do the adding
        of the node.

        :param node: The node to add to the scene.
        :param parent: The parent of the new node.
        """

        super().__init__()
        self._node = node
        self._parent = parent
        self._selected = False  # Was the node selected while the operation is undone? If so, we must re-select it when redoing it.

    def undo(self) -> None:
        """Reverses the operation of adding a scene node.

        This removes the scene node again.
        """

        self._node.setParent(None)
        self._selected = Selection.isSelected(self._node)
        if self._selected:
            Selection.remove(self._node)  # Also remove the node from the selection.

    def redo(self) -> None:
        """Re-applies this operation after it has been undone."""

        self._node.setParent(self._parent)
        if self._selected:  # It was selected while the operation was undone. We should restore that selection.
            Selection.add(self._node)
