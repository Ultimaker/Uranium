from . import SceneNode

from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Resources import Resources
from UM.Math.Color import Color

class ToolHandle(SceneNode.SceneNode):
    NoAxis = 1
    XAxis = 2
    YAxis = 3
    ZAxis = 4
    AllAxis = 5

    DisabledColor = Color(0.5, 0.5, 0.5, 1.0)
    XAxisColor = Color(1.0, 0.0, 0.0, 1.0)
    YAxisColor = Color(0.0, 0.0, 1.0, 1.0)
    ZAxisColor = Color(0.0, 1.0, 0.0, 1.0)
    AllAxisColor = Color(1.0, 1.0, 1.0, 1.0)

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

        renderer.queueNode(self, mode = Renderer.RenderLines, overlay = True, material = self._material)
        return True
