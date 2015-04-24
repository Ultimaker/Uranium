from . import SceneNode

from UM.Application import Application
from UM.View.Renderer import Renderer
from UM.Resources import Resources

class Platform(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

        self._settings = None
        self._material = None
        self._texture = None
        Application.getInstance().activeMachineChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()

        self.setCalculateBoundingBox(False)

    def render(self, renderer):
        if not self._material:
            self._material = renderer.createMaterial(
                Resources.getPath(Resources.ShadersLocation, 'default.vert'),
                Resources.getPath(Resources.ShadersLocation, 'platform.frag')
            )
            self._material.setUniformValue("u_ambientColor", [0.3, 0.3, 0.3, 1.0])
            self._material.setUniformValue("u_diffuseColor", [1.0, 1.0, 1.0, 1.0])
            self._material.setUniformValue('u_opacity', 0.5)
            if self._texture:
                self._material.setUniformTexture('u_texture', Resources.getPath(Resources.ImagesLocation, self._texture))

        if self.getMeshData():
            renderer.queueNode(self, material = self._material, transparent = True)
            return True

    def _onActiveMachineChanged(self):
        if self._settings:
            self.setMeshData(None)

        app = Application.getInstance()
        self._settings = app.getActiveMachine()
        if self._settings:
            mesh = self._settings.getPlatformMesh()
            self.setMeshData(app.getMeshFileHandler().read(Resources.getPath(Resources.MeshesLocation, mesh), app.getStorageDevice('LocalFileStorage'), center = False))
            self._texture = self._settings.getPlatformTexture()

            if self._material and self._texture:
                self._material.setUniformTexture('u_texture', Resources.getPath(Resources.ImagesLocation, self._texture))
