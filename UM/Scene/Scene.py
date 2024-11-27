# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import functools  # For partial to update files that were changed.
import os.path  # To watch files for changes.
import threading
from typing import Callable, List, Optional, Set, Any, Dict

from PyQt6.QtCore import QFileSystemWatcher  # To watch files for changes.

from UM.Logger import Logger
from UM.Mesh.ReadMeshJob import ReadMeshJob  # To reload a mesh when its file was changed.
from UM.Message import Message  # To display a message for reloading files that were changed.
from UM.Scene.Camera import Camera
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.SceneNode import SceneNode
from UM.Signal import Signal, signalemitter
from UM.i18n import i18nCatalog
from UM.Platform import Platform
if Platform.isWindows():
    from PyQt6.QtCore import QEventLoop  # Windows fix for using file watcher on removable devices.

i18n_catalog = i18nCatalog("uranium")
from time import time

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
        self._active_camera: Optional[Camera] = None
        self._ignore_scene_changes: bool = False
        self._lock = threading.Lock()

        # Watching file for changes.
        self._file_watcher = QFileSystemWatcher()
        self._file_watcher.fileChanged.connect(self._onFileChanged)

        self._reload_message: Optional[Message] = None

        # Need to keep these in memory. This is a memory leak every time you refresh, but a tiny one.
        self._callbacks: Set[Callable] = set()

        self._metadata: Dict[str, Any] = {}

    def setMetaDataEntry(self, key: str, entry: Any) -> None:
        self._metadata[key] = entry

    def clearMetaData(self):
        self._metadata = {}

    def getMetaData(self):
        return self._metadata.copy()

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

    def getRoot(self) -> SceneNode:
        """Get the root node of the scene."""

        return self._root

    def setRoot(self, node: SceneNode) -> None:
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

    def findObject(self, object_id: int) -> Optional[SceneNode]:
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

        # File watcher causes cura to crash on windows if threaded from removable device (usb, ...).
        # Create QEventLoop earlier to fix this.
        if Platform.isWindows():
            QEventLoop()
        self._file_watcher.addPath(file_path)

    def removeWatchedFile(self, file_path: str) -> None:
        """Remove a file so that it will no longer be watched for changes.

        :param file_path: The path to the file that must no longer be watched.
        """

        self._file_watcher.removePath(file_path)

    def _onFileChanged(self, file_path: str) -> None:
        """Triggered whenever a file is changed that we currently have loaded."""

        try:
            if os.path.getsize(file_path) == 0:  # File is empty.
                return
        except EnvironmentError:  # Or it doesn't exist anymore, or we have no access anymore.
            return

        # On Mac the reload file dialog would pop up for recently downloaded files, even if the file did not change
        # prevent such unwanted updates by checking if the modified time is recent enough, otherwise don't show a popup
        if Platform.isOSX() and time() - os.path.getmtime(file_path) > 10000:
            return

        from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
        modified_nodes = [node for node in DepthFirstIterator(self.getRoot()) if node.getMeshData() and node.getMeshData().getFileName() == file_path]  # type: ignore

        if modified_nodes:
            # Hide the message if it was already visible
            # Todo: keep one message for each modified file, when multiple had been updated at same time
            if self._reload_message is not None:
                self._reload_message.hide()

            self._reload_message = Message(i18n_catalog.i18nc("@info", "Would you like to reload {filename}?").format(
                                                filename = os.path.basename(file_path)),
                                            title = i18n_catalog.i18nc("@info:title", "File has been modified"))
            self._reload_message.addAction("reload", i18n_catalog.i18nc("@action:button", "Reload"),
                                           icon = "",
                                           description = i18n_catalog.i18nc("@action:description", "This will trigger the modified files to reload from disk."))
            self._reload_callback = functools.partial(self._reloadNodes, modified_nodes, file_path)
            self._reload_message.actionTriggered.connect(self._reload_callback)
            self._reload_message.show()

    def _reloadNodes(self, nodes: List["SceneNode"], file_path: str, message: str, action: str) -> None:
        """Reloads a list of nodes after the user pressed the "Reload" button.

        :param nodes: The list of nodes that needs to be reloaded.
        :param message: The message that triggered the action to reload them.
        :param action: The button that triggered the action to reload them.
        """

        if action != "reload":
            return
        if self._reload_message is not None:
            self._reload_message.hide()

        if not file_path or not os.path.isfile(file_path):  # File doesn't exist anymore.
            return

        job = ReadMeshJob(file_path)
        reload_finished_callback = functools.partial(self._reloadJobFinished, nodes)

        # Store it so it won't get garbage collected. This is a memory leak, but just one partial per reload so
        # it's not much.
        self._callbacks.add(reload_finished_callback)

        job.finished.connect(reload_finished_callback)
        job.start()

    def _reloadJobFinished(self, replaced_nodes: [SceneNode], job: ReadMeshJob) -> None:
        """Triggered when reloading has finished.

        This then puts the resulting mesh data in the nodes.
        Objects in the scene that are not in the reloaded file will be kept. (same as in the ReloadAll action)
        """
        renamed_nodes = {}  # type: Dict[str, int]

        for node in job.getResult():
            mesh_data = node.getMeshData()
            if not mesh_data:
                Logger.log("w", "Could not find a mesh in reloaded node.")
                continue

            # Solves issues with object naming
            node_name = node.getName()
            if not node_name:
                node_name = os.path.basename(mesh_data.getFileName())
            if node_name in renamed_nodes:  # objects may get renamed by Cura.UI.ObjectsModel._renameNodes() when loaded
                renamed_nodes[node_name] += 1
                node_name = "{0}({1})".format(node.getName(), renamed_nodes[node.getName()])
            else:
                renamed_nodes[node.getName()] = 0

            # Find the matching scene node to replace
            mesh_replaced = False
            for replaced_node in replaced_nodes:
                mesh_id = replaced_node.getMeshData().getMeshId()
                if mesh_id is None or mesh_id == mesh_data.getMeshId():
                    replaced_node.setMeshData(mesh_data)
                    mesh_replaced = True

            if not mesh_replaced:
                # Current node is a new one in the file, or it's ID has changed
                # TODO: Load this mesh into the scene. Also alter the "ReloadAll" action in CuraApplication.
                Logger.log("w", "Could not find matching node for object '{0}' in the scene.", node_name)
