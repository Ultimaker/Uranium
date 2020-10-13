# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional
from enum import IntEnum
import random

from UM.Logger import Logger
from UM.Mesh.MeshData import MeshData
from . import SceneNode

from UM.Resources import Resources
from UM.Application import Application
from UM.Math.Color import Color
from UM.Math.Vector import Vector

from UM.Scene.Selection import Selection

from UM.View.GL.OpenGL import OpenGL
from UM.View.RenderBatch import RenderBatch


class ToolHandle(SceneNode.SceneNode):
    """A tool handle is a object in the scene that gives queues for what the tool it is
    'paired' with can do. ToolHandles are, for example, used for translation, rotation & scale handles.
    They can also be used as actual objects to interact with (in the case of translation,
    pressing one arrow of the toolhandle locks the translation in that direction)
    """

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

    class ExtraWidgets(IntEnum):
        """Toolhandle subclasses can optionally register additional widgets by overriding this enum.
        The ExtraWidgetsEnum should start with Toolhanlde.AllAxis + 1 in order not to overlap with the native axes.
        """
        pass

    def __init__(self, parent = None):
        super().__init__(parent)

        self._disabled_axis_color = None
        self._x_axis_color = None
        self._y_axis_color = None
        self._z_axis_color = None
        self._all_axis_color = None

        self._axis_color_map = {}
        self._extra_widgets_color_map = {}

        self._scene = Application.getInstance().getController().getScene()

        self._solid_mesh = None  # type: Optional[MeshData]
        self._line_mesh = None  # type: Optional[MeshData]
        self._selection_mesh = None  # type: Optional[MeshData]
        self._shader = None

        self._active_axis = None  # type: Optional[int]

        # Auto scale is used to ensure that the tool handle will end up the same size on the camera no matter the zoom
        # This should be used to ensure that the tool handles are still usable even if the camera is zoomed in all the way.
        self._auto_scale = True

        self._enabled = False

        self.setCalculateBoundingBox(False)

        Selection.selectionCenterChanged.connect(self._onSelectionCenterChanged)
        Application.getInstance().engineCreatedSignal.connect(self._onEngineCreated)

    def getLineMesh(self) -> Optional[MeshData]:
        return self._line_mesh

    def setLineMesh(self, mesh: MeshData) -> None:
        self._line_mesh = mesh
        self.meshDataChanged.emit(self)

    def getSolidMesh(self) -> Optional[MeshData]:
        return self._solid_mesh

    def setSolidMesh(self, mesh: MeshData) -> None:
        self._solid_mesh = mesh
        self.meshDataChanged.emit(self)

    def getSelectionMesh(self) -> Optional[MeshData]:
        return self._selection_mesh

    def setSelectionMesh(self, mesh: MeshData) -> None:
        self._selection_mesh = mesh
        self.meshDataChanged.emit(self)

    def render(self, renderer) -> bool:
        if not self._enabled:
            return True

        if not self._shader:
            self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "toolhandle.shader"))

        if self._auto_scale:
            active_camera = self._scene.getActiveCamera()
            if active_camera.isPerspective():
                camera_position = active_camera.getWorldPosition()
                dist = (camera_position - self.getWorldPosition()).length()
                scale = dist / 400
            else:
                view_width = active_camera.getViewportWidth()
                current_size = view_width + (2 * active_camera.getZoomFactor() * view_width)
                scale = current_size / view_width * 5

            self.setScale(Vector(scale, scale, scale))

        if self._line_mesh:
            renderer.queueNode(self, mesh = self._line_mesh, mode = RenderBatch.RenderMode.Lines, overlay = True, shader = self._shader)
        if self._solid_mesh:
            renderer.queueNode(self, mesh = self._solid_mesh, overlay = True, shader = self._shader)

        return True

    def setActiveAxis(self, axis: Optional[int]) -> None:
        if axis == self._active_axis or not self._shader:
            return

        if axis:
            self._shader.setUniformValue("u_activeColor", self._axis_color_map.get(axis, Color()))
        else:
            self._shader.setUniformValue("u_activeColor", self._disabled_axis_color)
        self._active_axis = axis
        self._scene.sceneChanged.emit(self)

    def getActiveAxis(self) -> Optional[int]:
        return self._active_axis

    def isAxis(self, value):
        return value in self._axis_color_map

    def getExtraWidgetsColorMap(self):
        return self._extra_widgets_color_map

    def buildMesh(self) -> None:
        # This method should be overridden by toolhandle implementations
        pass

    def _onSelectionCenterChanged(self) -> None:
        if self._enabled:
            self.setPosition(Selection.getSelectionCenter())

    def setEnabled(self, enable: bool):
        super().setEnabled(enable)
        # Force an update
        self._onSelectionCenterChanged()

    def _onEngineCreated(self) -> None:
        from UM.Qt.QtApplication import QtApplication
        theme = QtApplication.getInstance().getTheme()
        if theme is None:
            Logger.log("w", "Could not get theme, so unable to create tool handle meshes.")
            return
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

        for value in self.ExtraWidgets:
            self._extra_widgets_color_map[value] = self._getUnusedColor()

        self.buildMesh()

    def _getUnusedColor(self):
        while True:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            a = 255
            color = Color(r, g, b, a)

            if color not in self._axis_color_map.values() and color not in self._extra_widgets_color_map.values():
                break

        return color