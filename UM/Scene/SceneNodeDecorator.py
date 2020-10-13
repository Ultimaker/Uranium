# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from UM.Scene.SceneNode import SceneNode


class SceneNodeDecorator:
    """The point of a SceneNodeDecorator is that it can be added to a SceneNode, where it then provides decorations
    Decorations are functions of a SceneNodeDecorator that can be called (except for functions already defined
    in SceneNodeDecorator).
    :sa SceneNode
    """

    def __init__(self, node: Optional["SceneNode"] = None) -> None:
        super().__init__()
        self._node = node  # type: Optional["SceneNode"]

    def setNode(self, node: "SceneNode") -> None:
        self._node = node

    def getNode(self) -> Optional["SceneNode"]:
        return self._node

    def clear(self) -> None:
        """Clear all data associated with this decorator. This will be called before the decorator is removed"""

        pass

    def __deepcopy__(self, memo: Dict[int, object]) -> "SceneNodeDecorator":
        raise NotImplementedError("Subclass {0} of SceneNodeDecorator should implement their own __deepcopy__() method.".format(str(self)))
