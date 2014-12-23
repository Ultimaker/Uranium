from . import SceneNode

from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Resources import Resources

class ToolHandle(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setMeshData(MeshData())
        self._material = None

    def render(self, renderer):
        if not self._material:
            self._material = renderer.createMaterial(
                Resources.getPath(Resources.ShadersLocation, 'basic.vert'),
                Resources.getPath(Resources.ShadersLocation, 'color.frag')
            )
            self._material.setUniformValue('u_color', [1.0, 0.0, 0.0, 1.0])

        renderer.queueMesh(self.getMeshData(), self.getGlobalTransformation(), mode = Renderer.RenderLines, overlay = True, material = self._material)
        return True
