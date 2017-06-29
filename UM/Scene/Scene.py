# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode
from UM.Scene.Camera import Camera
from UM.Signal import Signal, signalemitter
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

import threading


##  Container object for the scene graph.
#
#   The main purpose of this class is to provide the root SceneNode.
@signalemitter
class Scene():
    def __init__(self):
        super().__init__() # Call super to make multiple inheritance work.

        self._root = SceneNode(name= "Root")
        self._root.setCalculateBoundingBox(False)
        self._connectSignalsRoot()
        self._active_camera = None
        self._ignore_scene_changes = False
        self._lock = threading.Lock()

    def _connectSignalsRoot(self):
        self._root.transformationChanged.connect(self.sceneChanged)
        self._root.childrenChanged.connect(self.sceneChanged)
        self._root.meshDataChanged.connect(self.sceneChanged)

    def _disconnectSignalsRoot(self):
        self._root.transformationChanged.disconnect(self.sceneChanged)
        self._root.childrenChanged.disconnect(self.sceneChanged)
        self._root.meshDataChanged.disconnect(self.sceneChanged)

    def setIgnoreSceneChanges(self, ignore_scene_changes):
        if self._ignore_scene_changes != ignore_scene_changes:
            self._ignore_scene_changes = ignore_scene_changes
            if self._ignore_scene_changes:
                self._disconnectSignalsRoot()
            else:
                self._connectSignalsRoot()

    ##  Acquire the global scene lock.
    #
    #   This will prevent any read or write actions on the scene from other threads,
    #   assuming those threads also properly acquire the lock. Most notably, this
    #   prevents the rendering thread from rendering the scene while it is changing.
    #   Deprecated, use getSceneLock() instead.
    def acquireLock(self):
        self._lock.acquire()

    ##  Release the global scene lock.
    #   Deprecated, use getSceneLock() instead.
    def releaseLock(self):
        self._lock.release()

    ##  Gets the global scene lock.
    #
    #   Use this lock to prevent any read or write actions on the scene from other threads,
    #   assuming those threads also properly acquire the lock. Most notably, this
    #   prevents the rendering thread from rendering the scene while it is changing.
    def getSceneLock(self):
        return self._lock

    ##  Get the root node of the scene.
    def getRoot(self):
        return self._root

    ##  Change the root node of the scene
    def setRoot(self, node):
        if self._root != node:
            if not self._ignore_scene_changes:
                self._disconnectSignalsRoot()
            self._root = node
            if not self._ignore_scene_changes:
                self._connectSignalsRoot()
            self.rootChanged.emit()

    rootChanged = Signal()

    ##  Get the camera that should be used for rendering.
    def getActiveCamera(self):
        return self._active_camera

    def getAllCameras(self):
        cameras = []
        for node in BreadthFirstIterator(self._root):
            if isinstance(node, Camera):
                cameras.append(node)

        return cameras

    ##  Set the camera that should be used for rendering.
    #   \param name The name of the camera to use.
    def setActiveCamera(self, name):
        camera = self._findCamera(name)
        if camera:
            self._active_camera = camera

    ##  Signal. Emitted whenever something in the scene changes.
    #   \param object The object that triggered the change.
    sceneChanged = Signal()

    ##  Find an object by id.
    #
    #   \param object_id The id of the object to search for, as returned by the python id() method.
    #
    #   \return The object if found, or None if not.
    def findObject(self, object_id):
        for node in BreadthFirstIterator(self._root):
            if id(node) == object_id:
                return node
        return None

    ## private:
    def _findCamera(self, name):
        for node in BreadthFirstIterator(self._root):
            if isinstance(node, Camera) and node.getName() == name:
                return node
