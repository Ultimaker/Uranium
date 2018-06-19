# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import threading
from typing import Optional

from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.i18n import i18nCatalog
from UM.Decorators import deprecated

i18n_catalog = i18nCatalog("uranium")

MYPY = False
if MYPY:
    from UM.Scene.SceneNode import SceneNode


##  Container object for the scene graph
#
#   The main purpose of this class is to provide the root SceneNode.
class Scene:
    def __init__(self) -> None:
        super().__init__()  # Call super to make multiple inheritance work.

        from UM.Scene.SceneNode import SceneNode
        self._root = SceneNode(name= "Root")
        self._root.setCalculateBoundingBox(False)
        self._ignore_scene_changes = False
        self._lock = threading.Lock()

    def setIgnoreSceneChanges(self, ignore_scene_changes: bool) -> None:
        if self._ignore_scene_changes != ignore_scene_changes:
            self._ignore_scene_changes = ignore_scene_changes

    ##  Acquire the global scene lock.
    #
    #   This will prevent any read or write actions on the scene from other threads,
    #   assuming those threads also properly acquire the lock. Most notably, this
    #   prevents the rendering thread from rendering the scene while it is changing.
    #   Deprecated, use getSceneLock() instead.
    @deprecated("Please use the getSceneLock instead", "3.3")
    def acquireLock(self) -> None:
        self._lock.acquire()

    ##  Release the global scene lock.
    #   Deprecated, use getSceneLock() instead.
    @deprecated("Please use the getSceneLock instead", "3.3")
    def releaseLock(self) -> None:
        self._lock.release()

    ##  Gets the global scene lock.
    #
    #   Use this lock to prevent any read or write actions on the scene from other threads,
    #   assuming those threads also properly acquire the lock. Most notably, this
    #   prevents the rendering thread from rendering the scene while it is changing.
    def getSceneLock(self) -> threading.Lock:
        return self._lock

    ##  Get the root node of the scene.
    def getRoot(self) -> "SceneNode":
        return self._root

    ##  Change the root node of the scene
    def setRoot(self, node: "SceneNode") -> None:
        if self._root != node:
            self._root = node

    ##  Find an object by id.
    #
    #   \param object_id The id of the object to search for, as returned by the python id() method.
    #
    #   \return The object if found, or None if not.
    def findObject(self, object_id: int) -> Optional["SceneNode"]:
        for node in BreadthFirstIterator(self._root): #type: ignore
            if id(node) == object_id:
                return node
        return None
