# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import functools  # For partial to update files that were changed.
import os.path  # To watch files for changes.
import threading
from typing import Callable, List, Optional, Set

from PyQt5.QtCore import QFileSystemWatcher  # To watch files for changes.

from UM.Decorators import deprecated
from UM.Logger import Logger
from UM.Mesh.ReadMeshJob import ReadMeshJob  # To reload a mesh when its file was changed.
from UM.Message import Message  # To display a message for reloading files that were changed.
from UM.Scene.Camera import Camera
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.SceneNode import SceneNode
from UM.Signal import Signal, signalemitter
from UM.i18n import i18nCatalog
from UM.Platform import Platform

i18n_catalog = i18nCatalog("uranium")


@signalemitter
class Scene:
    """Container object for the scene graph

    The main purpose of this class is to provide the root SceneNode.
    """

    def __init__(self) -> None:
        super().__init__()

        from UM.Scene.SceneNode import SceneNode
        self._root = SceneNode(name = "Root")
        self._root.setCalculateBoundingBox(False)
        self._connectSignalsRoot()
        self._active_camera = None  # type: Optional[Camera]
        self._ignore_scene_changes = False
        self._lock = threading.Lock()

        # Watching file for changes.
        self._file_watcher = QFileSystemWatcher()
        self._file_watcher.fileChanged.connect(self._onFileChanged)

        self._reload_message = None  # type: Optional[Message]
        self._callbacks = set() # type: Set[Callable] # Need to keep these in memory. This is a memory leak every time you refresh, but a tiny one.

    def _connectSignalsRoot(self) -> None:
        self._root.transformationChanged.connect(self.sceneChanged)
        self._root.childrenChanged.connect(self.sceneChanged)
        self._root.meshDataChanged.connect(self.sceneChanged)

    def _disconnectSignalsRoot(self) -> None:
        self._root.transformationChanged.disconnect(self.sceneChanged)
        self._root.childrenChanged.disconnect(self.sceneChanged)
        self._root.meshDataChanged.disconnect(self.sceneChanged)

    def setIgnoreSceneChanges(self, ignore_scene_changes: bool) -> None:
        if self._ignore_scene_changes != ignore_scene_changes:
            self._ignore_scene_changes = ignore_scene_changes
            if self._ignore_scene_changes:
                self._disconnectSignalsRoot()
            else:
                self._connectSignalsRoot()

    @deprecated("Scene lock is no longer used", "4.5")
    def getSceneLock(self) -> threading.Lock:
        return self._lock

    def getRoot(self) -> "SceneNode":
        """Get the root node of the scene."""

        return self._root

    def setRoot(self, node: "SceneNode") -> None:
        """Change the root node of the scene"""

        if self._root != node:
            if not self._ignore_scene_changes:
                self._disconnectSignalsRoot()
            self._root = node
            if not self._ignore_scene_changes:
                self._connectSignalsRoot()
            self.rootChanged.emit()

    rootChanged = Signal()

    def getActiveCamera(self) -> Optional[Camera]:
        """Get the camera that should be used for rendering."""

        return self._active_camera

    def getAllCameras(self) -> List[Camera]:
        cameras = []
        for node in BreadthFirstIterator(self._root):
            if isinstance(node, Camera):
                cameras.append(node)
        return cameras

    def setActiveCamera(self, name: str) -> None:
        """Set the camera that should be used for rendering.

        :param name: The name of the camera to use.
        """

        camera = self.findCamera(name)
        if camera and camera != self._active_camera:
            if self._active_camera:
                self._active_camera.perspectiveChanged.disconnect(self.sceneChanged)
            self._active_camera = camera
            self._active_camera.perspectiveChanged.connect(self.sceneChanged)
        else:
            Logger.log("w", "Couldn't find camera with name [%s] to activate!" % name)

    sceneChanged = Signal()
    """Signal that is emitted whenever something in the scene changes.

    :param object: The object that triggered the change.
    """

    def findObject(self, object_id: int) -> Optional["SceneNode"]:
        """Find an object by id.

        :param object_id: The id of the object to search for, as returned by the python id() method.

        :return: The object if found, or None if not.
        """

        for node in BreadthFirstIterator(self._root):
            if id(node) == object_id:
                return node
        return None

    def findCamera(self, name: str) -> Optional[Camera]:
        for node in BreadthFirstIterator(self._root):
            if isinstance(node, Camera) and node.getName() == name:
                return node
        return None

    def addWatchedFile(self, file_path: str) -> None:
        """Add a file to be watched for changes.

        :param file_path: The path to the file that must be watched.
        """

        # The QT 5.10.0 issue, only on Windows. Cura crashes after loading a stl file from USB/sd-card/Cloud-based drive
        if not Platform.isWindows():
            self._file_watcher.addPath(file_path)

    def removeWatchedFile(self, file_path: str) -> None:
        """Remove a file so that it will no longer be watched for changes.

        :param file_path: The path to the file that must no longer be watched.
        """

        # The QT 5.10.0 issue, only on Windows. Cura crashes after loading a stl file from USB/sd-card/Cloud-based drive
        if not Platform.isWindows():
            self._file_watcher.removePath(file_path)

    def _onFileChanged(self, file_path: str) -> None:
        """Triggered whenever a file is changed that we currently have loaded."""

        try:
            if os.path.getsize(file_path) == 0:  # File is empty.
                return
        except EnvironmentError:  # Or it doesn't exist any more, or we have no access any more.
            return

        # Multiple nodes may be loaded from the same file at different stages. Reload them all.
        from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator  # To find which nodes to reload when files have changed.
        modified_nodes = [node for node in DepthFirstIterator(self.getRoot()) if node.getMeshData() and node.getMeshData().getFileName() == file_path]  # type: ignore

        if modified_nodes:
            # Hide the message if it was already visible
            if self._reload_message is not None:
                self._reload_message.hide()

            self._reload_message = Message(i18n_catalog.i18nc("@info", "Would you like to reload {filename}?").format(filename = os.path.basename(file_path)),
                              title = i18n_catalog.i18nc("@info:title", "File has been modified"))
            self._reload_message.addAction("reload", i18n_catalog.i18nc("@action:button", "Reload"), icon = "", description = i18n_catalog.i18nc("@action:description", "This will trigger the modified files to reload from disk."))
            self._reload_callback = functools.partial(self._reloadNodes, modified_nodes)
            self._reload_message.actionTriggered.connect(self._reload_callback)
            self._reload_message.show()

    def _reloadNodes(self, nodes: List["SceneNode"], message: str, action: str) -> None:
        """Reloads a list of nodes after the user pressed the "Reload" button.

        :param nodes: The list of nodes that needs to be reloaded.
        :param message: The message that triggered the action to reload them.
        :param action: The button that triggered the action to reload them.
        """

        if action != "reload":
            return
        if self._reload_message is not None:
            self._reload_message.hide()
        for node in nodes:
            meshdata = node.getMeshData()
            if meshdata:
                filename = meshdata.getFileName()
                if not filename or not os.path.isfile(filename):  # File doesn't exist any more.
                    continue
                job = ReadMeshJob(filename)
                reload_finished_callback = functools.partial(self._reloadJobFinished, node)
                self._callbacks.add(reload_finished_callback) #Store it so it won't get garbage collected. This is a memory leak, but just one partial per reload so it's not much.
                job.finished.connect(reload_finished_callback)
                job.start()

    def _reloadJobFinished(self, replaced_node: SceneNode, job: ReadMeshJob) -> None:
        """Triggered when reloading has finished.

        This then puts the resulting mesh data in the node.
        """

        for node in job.getResult():
            mesh_data = node.getMeshData()
            if mesh_data:
                replaced_node.setMeshData(mesh_data)
            else:
                Logger.log("w", "Could not find a mesh in reloaded node.")