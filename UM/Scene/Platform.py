# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import SceneNode

from UM.Application import Application
from UM.View.Renderer import Renderer
from UM.Resources import Resources
from UM.Math.Vector import Vector

from UM.View.GL.OpenGL import OpenGL

class Platform(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

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
            meshData = None
            mesh = self._machine_instance.getMachineDefinition().getPlatformMesh()
            if mesh:
                path = Resources.getPath(Resources.Meshes, mesh)
                reader = app.getMeshFileHandler().getReaderForFile(path)
                _meshData = app.getMeshFileHandler().readerRead(reader, path, center = False)
                if _meshData:
                    meshData = _meshData.getMeshData()
            self.setMeshData(meshData)

            self._updateTexture()

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
