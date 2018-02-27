# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import functools #For partial to update files that were changed.
import os.path #To watch files for changes.
from PyQt5.QtCore import QFileSystemWatcher #To watch files for changes.
import threading

from UM.i18n import i18nCatalog
from UM.Logger import Logger
from UM.Mesh.ReadMeshJob import ReadMeshJob #To reload a mesh when its file was changed.
from UM.Message import Message #To display a message for reloading files that were changed.
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator #To find which nodes to reload when files have changed.
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Camera import Camera
from UM.Signal import Signal, signalemitter
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

i18n_catalog = i18nCatalog("uranium")

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

        #Watching file for changes.
        self._file_watcher = QFileSystemWatcher()
        self._file_watcher.fileChanged.connect(self._onFileChanged)

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
        camera = self.findCamera(name)
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

    def findCamera(self, name):
        for node in BreadthFirstIterator(self._root):
            if isinstance(node, Camera) and node.getName() == name:
                return node

    ##  Add a file to be watched for changes.
    #   \param file_path The path to the file that must be watched.
    def addWatchedFile(self, file_path):
        self._file_watcher.addPath(file_path)

    ##  Remove a file so that it will no longer be watched for changes.
    #   \param file_path The path to the file that must no longer be watched.
    def removeWatchedFile(self, file_path):
        self._file_watcher.removePath(file_path)

    ##  Triggered whenever a file is changed that we currently have loaded.
    def _onFileChanged(self, file_path):
        if not os.path.isfile(self.file_path): #File doesn't exist any more.
            return

        #Multiple nodes may be loaded from the same file at different stages. Reload them all.
        modified_nodes = (node for node in DepthFirstIterator(self.getRoot()) if node.getMeshData() and node.getMeshData().getFileName() == file_path)

        if modified_nodes:
            message = Message(i18n_catalog.i18nc("@info", "Would you like to reload {filename}?").format(filename = os.path.basename(self._file_name)),
                              title = i18n_catalog.i18nc("@info:title", "File has been modified"))
            message.addAction("reload", i18n_catalog.i18nc("@action:button", "Reload"), icon = None, description = i18n_catalog.i18nc("@action:description", "This will trigger the modified files to reload from disk."))
            message.actionTriggered.connect(functools.partialmethod(self._reloadNodes, modified_nodes))
            message.show()

    ##  Reloads a list of nodes after the user pressed the "Reload" button.
    #   \param nodes The list of nodes that needs to be reloaded.
    #   \param message The message that triggered the action to reload them.
    #   \param action The button that triggered the action to reload them.
    def _reloadNodes(self, nodes, message, action):
        if action != "reload":
            return
        for node in nodes:
            if not os.path.isfile(node.getMeshData().getFileName()): #File doesn't exist any more.
                continue
            job = ReadMeshJob(node.getMeshData().getFileName())
            job._node = node
            job.finished.connect(self._reloadJobFinished)
            job.start()

    ##  Triggered when reloading has finished.
    #
    #   This then puts the resulting mesh data in the node.
    def _reloadJobFinished(self, job):
        for node in job.getResult():
            mesh_data = node.getMeshData()
            if mesh_data:
                job._node.setMeshData(mesh_data)
            else:
                Logger.log("w", "Could not find a mesh in reloaded node.")