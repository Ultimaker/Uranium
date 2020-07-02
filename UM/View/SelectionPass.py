# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import enum
import random
from typing import TYPE_CHECKING

from UM.Resources import Resources
from UM.Application import Application

from UM.Math.Color import Color

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.View.RenderPass import RenderPass
from UM.View.RenderBatch import RenderBatch
from UM.View.GL.OpenGL import OpenGL

if TYPE_CHECKING:
    from UM.Scene.SceneNode import SceneNode

class SelectionPass(RenderPass):
    """A RenderPass subclass responsible for rendering selectable objects to a texture.

    This pass performs the rendering of selectable objects to a texture that can be
    sampled to retrieve the actual object that was underneath the mouse cursor. Additionally,
    information about what objects are actually selected is rendered into the alpha channel
    of this render pass so it can be used later on in the composite pass.
    """
    class SelectionMode(enum.Enum):
        OBJECTS = "objects"
        FACES = "faces"

    def __init__(self, width, height):
        super().__init__("selection", width, height, -999)

        self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "selection.shader"))
        self._face_shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "select_face.shader"))
        self._tool_handle_shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "default.shader"))
        self._gl = OpenGL.getInstance().getBindingsObject()
        self._scene = Application.getInstance().getController().getScene()

        self._renderer = Application.getInstance().getRenderer()

        self._selection_map = {}
        self._default_toolhandle_selection_map = {
            self._dropAlpha(ToolHandle.DisabledSelectionColor): ToolHandle.NoAxis,
            self._dropAlpha(ToolHandle.XAxisSelectionColor): ToolHandle.XAxis,
            self._dropAlpha(ToolHandle.YAxisSelectionColor): ToolHandle.YAxis,
            self._dropAlpha(ToolHandle.ZAxisSelectionColor): ToolHandle.ZAxis,
            self._dropAlpha(ToolHandle.AllAxisSelectionColor): ToolHandle.AllAxis,
            ToolHandle.DisabledSelectionColor: ToolHandle.NoAxis,
            ToolHandle.XAxisSelectionColor: ToolHandle.XAxis,
            ToolHandle.YAxisSelectionColor: ToolHandle.YAxis,
            ToolHandle.ZAxisSelectionColor: ToolHandle.ZAxis,
            ToolHandle.AllAxisSelectionColor: ToolHandle.AllAxis
        }
        self._toolhandle_selection_map = {}
        Application.getInstance().getController().activeToolChanged.connect(self._onActiveToolChanged)
        self._onActiveToolChanged()

        self._mode = SelectionPass.SelectionMode.OBJECTS
        Selection.selectedFaceChanged.connect(self._onSelectedFaceChanged)

        self._output = None

    def _onActiveToolChanged(self):
        self._toolhandle_selection_map = self._default_toolhandle_selection_map.copy()

        active_tool = Application.getInstance().getController().getActiveTool()
        if not active_tool:
            return

        tool_handle = active_tool.getHandle()
        if not tool_handle:
            return
        for name, color in tool_handle.getExtraWidgetsColorMap().items():
            self._toolhandle_selection_map[color] = name
            self._toolhandle_selection_map[self._dropAlpha(color)] = name

    def _onSelectedFaceChanged(self):
        self._mode = SelectionPass.SelectionMode.FACES if Selection.getFaceSelectMode() else SelectionPass.SelectionMode.OBJECTS

    def render(self):
        """Perform the actual rendering."""
        if self._mode == SelectionPass.SelectionMode.OBJECTS:
            self._renderObjectsMode()
        elif self._mode == SelectionPass.SelectionMode.FACES:
            self._renderFacesMode()

    def _renderObjectsMode(self):
        self._selection_map = self._toolhandle_selection_map.copy()

        batch = RenderBatch(self._shader)
        tool_handle = RenderBatch(self._tool_handle_shader, type = RenderBatch.RenderType.Overlay)
        selectable_objects = False
        for node in DepthFirstIterator(self._scene.getRoot()):
            if isinstance(node, ToolHandle):
                tool_handle.addItem(node.getWorldTransformation(copy = False), mesh = node.getSelectionMesh())
                continue

            if node.isSelectable() and node.getMeshData():
                selectable_objects = True
                batch.addItem(transformation = node.getWorldTransformation(copy = False), mesh = node.getMeshData(), uniforms = { "selection_color": self._getNodeColor(node)}, normal_transformation=node.getCachedNormalMatrix())

        self.bind()
        if selectable_objects:
            batch.render(self._scene.getActiveCamera())

            self._gl.glColorMask(self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_FALSE)
            self._gl.glDisable(self._gl.GL_DEPTH_TEST)

            tool_handle.render(self._scene.getActiveCamera())

            self._gl.glEnable(self._gl.GL_DEPTH_TEST)
            self._gl.glColorMask(self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_TRUE)

        self.release()

    def _renderFacesMode(self):
        batch = RenderBatch(self._face_shader)

        selectable_objects = False
        for node in Selection.getAllSelectedObjects():
            if isinstance(node, ToolHandle):
                continue  # Ignore tool-handles in this mode.

            if node.isSelectable() and node.getMeshData():
                selectable_objects = True
                batch.addItem(transformation = node.getWorldTransformation(copy = False), mesh = node.getMeshData(), normal_transformation=node.getCachedNormalMatrix())

        self.bind()
        if selectable_objects:
            batch.render(self._scene.getActiveCamera())

        self.release()

    def getIdAtPosition(self, x, y):
        """Get the object id at a certain pixel coordinate."""
        output = self.getOutput()

        window_size = self._renderer.getWindowSize()

        px = (0.5 + x / 2.0) * window_size[0]
        py = (0.5 + y / 2.0) * window_size[1]

        if px < 0 or px > (output.width() - 1) or py < 0 or py > (output.height() - 1):
            return None

        pixel = output.pixel(px, py)
        return self._selection_map.get(Color.fromARGB(pixel), None)

    def getFaceIdAtPosition(self, x, y):
        """Get an unique identifier to the face of the polygon at a certain pixel-coordinate."""
        output = self.getOutput()

        window_size = self._renderer.getWindowSize()

        px = (0.5 + x / 2.0) * window_size[0]
        py = (0.5 + y / 2.0) * window_size[1]

        if px < 0 or px > (output.width() - 1) or py < 0 or py > (output.height() - 1):
            return -1

        face_color = Color.fromARGB(output.pixel(px, py))
        if int(face_color.b * 255) % 2 == 0:
            return -1
        return (
            ((int(face_color.b * 255.) - 1) << 15) |
            (int(face_color.g * 255.) << 8) |
            int(face_color.r * 255.)
        )

    def _getNodeColor(self, node):
        while True:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            a = 255 if Selection.isSelected(node) or self._isInSelectedGroup(node) else 0
            color = Color(r, g, b, a)

            if color not in self._selection_map:
                break

        self._selection_map[color] = id(node)

        return color

    def _dropAlpha(self, color):
        return Color(color.r, color.g, color.b, 0.0)

    def _isInSelectedGroup(self, node: "SceneNode") -> bool:
        """
        Get whether the given node is in a group that is selected.
        :param node: The node to check.
        :return: ``True`` if the node is in a selected group, or ``False`` if
        it's not.
        """
        group_node = node.getParent()
        if group_node is None:  # Separate node that's not in the scene.
            return False  # Can never get selected.
        while group_node.callDecoration("isGroup"):
            if Selection.isSelected(group_node):
                return True
            group_node = group_node.getParent()
            if group_node is None:
                return False
        return False
