from . import SceneNode

from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Resources import Resources
from UM.Application import Application
from UM.Math.Color import Color
from UM.Math.Vector import Vector

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

        self._scene = Application.getInstance().getController().getScene()

        self._solid_mesh = None
        self._line_mesh = None
        self._selection_mesh = None
        self._material = None

        self._previous_dist = None
        self._active_axis = None

    def getLineMesh(self):
        return self._line_mesh

    def setLineMesh(self, mesh):
        self._line_mesh = mesh

    def getSolidMesh(self):
        return self._solid_mesh

    def setSolidMesh(self, mesh):
        self._solid_mesh = mesh

    def getSelectionMesh(self):
        return self._selection_mesh

    def setSelectionMesh(self, mesh):
        self._selection_mesh = mesh

    def getMaterial(self):
        return self._material

    def render(self, renderer):
        if not self._material:
            self._material = renderer.createMaterial(
                Resources.getPath(Resources.ShadersLocation, 'toolhandle.vert'),
                Resources.getPath(Resources.ShadersLocation, 'toolhandle.frag')
            )
            self._material.setUniformValue('u_disabledColor', self.DisabledColor)
            self._material.setUniformValue('u_activeColor', self.DisabledColor)

        camera_position = self._scene.getActiveCamera().getWorldPosition()
        dist = (camera_position - self.getWorldPosition()).length()

        scale = dist / 200
        self.setScale(Vector(scale, scale, scale))

        if self._line_mesh:
            renderer.queueNode(self, mesh = self._line_mesh, mode = Renderer.RenderLines, overlay = True, material = self._material)
        if self._solid_mesh:
            renderer.queueNode(self, mesh = self._solid_mesh, mode = Renderer.RenderTriangles, overlay = True, material = self._material)
        return True

    def getSelectionMap(self):
        return {
            self.XAxisColor: self.XAxis,
            self.YAxisColor: self.YAxis,
            self.ZAxisColor: self.ZAxis,
            self.AllAxisColor: self.AllAxis
        }

    def setActiveAxis(self, axis):
        if axis == self._active_axis or not self._material:
            return

        if axis:
            self._material.setUniformValue('u_activeColor', self._axisColorMap[axis])
        else:
            self._material.setUniformValue('u_activeColor', self.DisabledColor)
        self._active_axis = axis
        self._scene.sceneChanged.emit(self)

    @classmethod
    def isAxis(cls, value):
        return value in cls._axisColorMap

    _axisColorMap = {
        NoAxis: DisabledColor,
        XAxis: XAxisColor,
        YAxis: YAxisColor,
        ZAxis: ZAxisColor,
        AllAxis: AllAxisColor
    }
