from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from UM.Scene.Selection import Selection
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from UM.Scene.SceneNode import SceneNode


class GroupDecorator(SceneNodeDecorator):
    def __init__(self, remove_when_empty: bool = True) -> None:
        super().__init__()
        # Used to keep track of previous parent when an empty group removes itself from the scene.
        # We keep this option so that it's possible to undo it.
        self._old_parent = None  # type: Optional[SceneNode]
        self._remove_when_empty = remove_when_empty

    def setNode(self, node: "SceneNode") -> None:
        super().setNode(node)
        if self._node is not None:
            self._node.childrenChanged.connect(self._onChildrenChanged)

    def isGroup(self) -> bool:
        return True

    def getOldParent(self) -> Optional["SceneNode"]:
        return self._old_parent

    def _onChildrenChanged(self, node: "SceneNode") -> None:
        if self._node is None:
            return
        if not self._remove_when_empty:
            return

        if not self._node.hasChildren():
            # A group that no longer has children may remove itself from the scene
            self._old_parent = self._node.getParent()
            self._node.setParent(None)
            Selection.remove(self._node)
        else:
            # A group that has removed itself from the scene because it had no children may add itself back to the scene
            # when a child is added to it.
            if not self._node.getParent() and self._old_parent:
                self._node.setParent(self._old_parent)
                self._old_parent = None

    def __deepcopy__(self, memo):
        return GroupDecorator()