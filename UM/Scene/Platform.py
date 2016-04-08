# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import SceneNode

from UM.Application import Application
from UM.Resources import Resources
from UM.Math.Vector import Vector
from UM.Job import Job

from UM.View.GL.OpenGL import OpenGL


class Platform(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

        self._load_platform_job = None
        self._machine_instance = None
        self._shader = None
        self._texture = None
        Application.getInstance().getMachineManager().activeMachineInstanceChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()

        self.setCalculateBoundingBox(False)

    def render(self, renderer):
        if not self._shader:
            self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "platform.shader"))
            if self._texture:
                self._shader.setTexture(0, self._texture)
            else:
                self._updateTexture()

        if self.getMeshData():
            renderer.queueNode(self, shader = self._shader, transparent = True, backface_cull = True, sort = -10)
            return True

    def _onActiveMachineChanged(self):
        if self._machine_instance:
            self.setMeshData(None)

        app = Application.getInstance()
        self._machine_instance = app.getMachineManager().getActiveMachineInstance()
        if self._machine_instance:
            mesh_file = self._machine_instance.getMachineDefinition().getPlatformMesh()
            if mesh_file:
                path = Resources.getPath(Resources.Meshes, mesh_file)

                if self._load_platform_job:
                    #This prevents a previous load job from triggering texture loads.
                    self._load_platform_job.finished.disconnect(self._onPlatformLoaded)

                # Perform platform mesh loading in the background
                self._load_platform_job = _LoadPlatformJob(path)
                self._load_platform_job.finished.connect(self._onPlatformLoaded)
                self._load_platform_job.start()

            offset = self._machine_instance.getSettingValue("machine_platform_offset")
            if offset:
                self.setPosition(Vector(offset[0], offset[1], offset[2]))
            else:
                self.setPosition(Vector(0.0, 0.0, 0.0))

    def _updateTexture(self):
        if not self._machine_instance or not OpenGL.getInstance():
            return

        texture_file = self._machine_instance.getMachineDefinition().getPlatformTexture()
        if texture_file:
            self._texture = OpenGL.getInstance().createTexture()
            self._texture.load(Resources.getPath(Resources.Images, texture_file))

            if self._shader:
                self._shader.setTexture(0, self._texture)
        else:
            self._texture = None
            if self._shader:
                self._shader.setTexture(0, None)

    def _onPlatformLoaded(self, job):
        self._load_platform_job = None

        if not job.getResult():
            self.setMeshData(None)
            return

        node = job.getResult()
        if node.getMeshData():
            self.setMeshData(node.getMeshData())

            Application.getInstance().callLater(self._updateTexture) #Calling later because for some reason the OpenGL context might be outdated on some computers.

class _LoadPlatformJob(Job):
    def __init__(self, file_name):
        self._file_name = file_name
        self._mesh_handler = Application.getInstance().getMeshFileHandler()

    def run(self):
        reader = self._mesh_handler.getReaderForFile(self._file_name)
        if not reader:
            self.setResult(None)
            return

        self.setResult(reader.read(self._file_name))
