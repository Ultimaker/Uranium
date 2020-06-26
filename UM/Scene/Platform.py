# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import SceneNode

from UM.Application import Application
from UM.Logger import Logger
from UM.Resources import Resources
from UM.Math.Vector import Vector
from UM.Job import Job
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.View.GL.OpenGL import OpenGL


class Platform(SceneNode.SceneNode):
    """Platform is a special case of Scene node. It renders a specific model as the platform of the machine.
    A specialised class is used due to the differences in how it needs to rendered and the fact that a platform
    can have a Texture.
    It also handles the re-loading of the mesh when the active machine is changed.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self._load_platform_job = None
        self._shader = None
        self._texture = None
        self._global_container_stack = None
        Application.getInstance().globalContainerStackChanged.connect(self._onGlobalContainerStackChanged)
        self._onGlobalContainerStackChanged()
        self.setCalculateBoundingBox(False)

    def render(self, renderer):
        if not self.isVisible():
            return True
        if not self._shader:
            self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "platform.shader"))
            if self._texture:
                self._shader.setTexture(0, self._texture)
            else:
                self._updateTexture()

        if self.getMeshData():
            renderer.queueNode(self, shader = self._shader, transparent = True, backface_cull = True, sort = -10)
            return True

    def _onGlobalContainerStackChanged(self):
        if self._global_container_stack:
            self.setMeshData(None)

        self._global_container_stack = Application.getInstance().getGlobalContainerStack()
        if self._global_container_stack:
            container = self._global_container_stack.findContainer({ "platform": "*" })
            if container:
                mesh_file = container.getMetaDataEntry("platform")
                try:
                    path = Resources.getPath(Resources.Meshes, mesh_file)
                except FileNotFoundError:
                    Logger.log("w", "Unable to find the platform mesh %s", mesh_file)
                    path = ""

                if self._load_platform_job:
                    # This prevents a previous load job from triggering texture loads.
                    self._load_platform_job.finished.disconnect(self._onPlatformLoaded)

                # Perform platform mesh loading in the background
                self._load_platform_job = _LoadPlatformJob(path)
                self._load_platform_job.finished.connect(self._onPlatformLoaded)
                self._load_platform_job.start()

                offset = container.getMetaDataEntry("platform_offset")
                if offset:
                    if len(offset) == 3:
                        self.setPosition(Vector(offset[0], offset[1], offset[2]))
                    else:
                        Logger.log("w", "Platform offset is invalid: %s", str(offset))
                        self.setPosition(Vector(0.0, 0.0, 0.0))
                else:
                    self.setPosition(Vector(0.0, 0.0, 0.0))

    def _updateTexture(self):
        if not self._global_container_stack or not OpenGL.getInstance():
            return

        self._texture = OpenGL.getInstance().createTexture()

        container = self._global_container_stack.findContainer({"platform_texture": "*"})
        if container:
            texture_file = container.getMetaDataEntry("platform_texture")
            try:
                self._texture.load(Resources.getPath(Resources.Images, texture_file))
            except FileNotFoundError:
                Logger.log("w", "Unable to find platform texture [%s] as specified in the definition", texture_file)
        # Note: if no texture file is specified, a 1 x 1 pixel transparent image is created
        # by UM.GL.QtTexture to prevent rendering issues

        if self._shader:
            self._shader.setTexture(0, self._texture)

    def _onPlatformLoaded(self, job):
        self._load_platform_job = None

        if not job.getResult():
            self.setMeshData(None)
            return

        node = job.getResult()
        if isinstance(node, list):  # Some model readers return lists of models. Some (e.g. STL) return a list SOMETIMES but not always.
            nodelist = [actual_node for subnode in node for actual_node in DepthFirstIterator(subnode) if actual_node.getMeshData()]
            node = max(nodelist, key = lambda n: n.getMeshData().getFaceCount())  # Select the node with the most faces. Sometimes the actual node is a child node of something. We can only have one node as platform mesh.
        if node.getMeshData():
            self.setMeshData(node.getMeshData())

            # Calling later because for some reason the OpenGL context might be outdated on some computers.
            Application.getInstance().callLater(self._updateTexture)


class _LoadPlatformJob(Job):
    """Protected class that ensures that the mesh for the machine platform is loaded."""

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name
        self._mesh_handler = Application.getInstance().getMeshFileHandler()

    def run(self):
        reader = self._mesh_handler.getReaderForFile(self._file_name)
        if not reader:
            self.setResult(None)
            return

        self.setResult(reader.read(self._file_name))
