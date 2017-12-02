# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import SceneNode

from UM.Resources import Resources
from UM.Application import Application
from UM.Math.Color import Color
from UM.Math.Vector import Vector

from UM.Scene.Selection import Selection

from UM.View.GL.OpenGL import OpenGL
from UM.View.RenderBatch import RenderBatch


##    A tool handle is a object in the scene that gives queues for what the tool it is
#     'paired' with can do. ToolHandles are used for translation, rotation & scale handles.
#     They can also be used as actual objects to interact with (in the case of translation,
#     pressing one arrow of the toolhandle locks the translation in that direction)
class ToolHandle(SceneNode.SceneNode):
    NoAxis = 1
    XAxis = 2
    YAxis = 3
    ZAxis = 4
    AllAxis = 5

    # These colors are used to draw the selection pass only. They must be unique, which is
    # why we cannot rely on themed colors
    DisabledSelectionColor = Color(0.5, 0.5, 0.5, 1.0)
    XAxisSelectionColor = Color(1.0, 0.0, 0.0, 1.0)
    YAxisSelectionColor = Color(0.0, 0.0, 1.0, 1.0)
    ZAxisSelectionColor = Color(0.0, 1.0, 0.0, 1.0)
    AllAxisSelectionColor = Color(1.0, 1.0, 1.0, 1.0)

    def __init__(self, parent = None):
        super().__init__(parent)

        self._disabled_axis_color = None
        self._x_axis_color = None
        self._y_axis_color = None
        self._z_axis_color = None
        self._all_axis_color = None

        self._axis_color_map = {}

        self._scene = Application.getInstance().getController().getScene()

        self._solid_mesh = None
        self._line_mesh = None
        self._selection_mesh = None
        self._shader = None

        self._previous_dist = None
        self._active_axis = None
        self._auto_scale = True

        self.setCalculateBoundingBox(False)

        Selection.selectionCenterChanged.connect(self._onSelectionCenterChanged)
        Application.getInstance().engineCreatedSignal.connect(self._onEngineCreated)

    def getLineMesh(self):
        return self._line_mesh

    def setLineMesh(self, mesh):
        self._line_mesh = mesh
        self.meshDataChanged.emit(self)

    def getSolidMesh(self):
        return self._solid_mesh

    def setSolidMesh(self, mesh):
        self._solid_mesh = mesh
        self.meshDataChanged.emit(self)

    def getSelectionMesh(self):
        return self._selection_mesh

    def setSelectionMesh(self, mesh):
        self._selection_mesh = mesh
        self.meshDataChanged.emit(self)

    def getMaterial(self):
        return self._shader

    def render(self, renderer):
        if not self._shader:
            self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "toolhandle.shader"))

        if self._auto_scale:
            camera_position = self._scene.getActiveCamera().getWorldPosition()
            dist = (camera_position - self.getWorldPosition()).length()
            scale = dist / 400
            self.setScale(Vector(scale, scale, scale))

        if self._line_mesh:
            renderer.queueNode(self, mesh = self._line_mesh, mode = RenderBatch.RenderMode.Lines, overlay = True, shader = self._shader)
        if self._solid_mesh:
            renderer.queueNode(self, mesh = self._solid_mesh, overlay = True, shader = self._shader)

        return True

    def setActiveAxis(self, axis):
        if axis == self._active_axis or not self._shader:
            return

        if axis:
            self._shader.setUniformValue("u_activeColor", self._axis_color_map[axis])
        else:
            self._shader.setUniformValue("u_activeColor", self._disabled_axis_color)
        self._active_axis = axis
        self._scene.sceneChanged.emit(self)

    def isAxis(self, value):
        return value in self._axis_color_map

    def buildMesh(self):
        # This method should be overridden by toolhandle implementations
        pass

    def _onSelectionCenterChanged(self):
        self.setPosition(Selection.getSelectionCenter())

    def _onEngineCreated(self):
        theme = Application.getInstance().getTheme()
        self._disabled_axis_color = Color(*theme.getColor("disabled_axis").getRgb())
        self._x_axis_color = Color(*theme.getColor("x_axis").getRgb())
        self._y_axis_color = Color(*theme.getColor("y_axis").getRgb())
        self._z_axis_color = Color(*theme.getColor("z_axis").getRgb())
        self._all_axis_color = Color(*theme.getColor("all_axis").getRgb())

        self._axis_color_map = {
            self.NoAxis: self._disabled_axis_color,
            self.XAxis: self._x_axis_color,
            self.YAxis: self._y_axis_color,
            self.ZAxis: self._z_axis_color,
            self.AllAxis: self._all_axis_color
        }

        self.buildMesh()