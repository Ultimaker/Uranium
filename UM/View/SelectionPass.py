# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import random

from UM.Resources import Resources
from UM.Application import Application

from UM.Math.Color import Color

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.View.RenderPass import RenderPass
from UM.View.RenderBatch import RenderBatch
from UM.View.GL.OpenGL import OpenGL


##  A RenderPass subclass responsible for rendering selectable objects to a texture.
#
#   This pass performs the rendering of selectable objects to a texture that can be
#   sampled to retrieve the actual object that was underneath the mouse cursor. Additionally,
#   information about what objects are actually selected is rendered into the alpha channel
#   of this render pass so it can be used later on in the composite pass.
class SelectionPass(RenderPass):
    def __init__(self, width, height):
        super().__init__("selection", width, height, -999)

        self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "selection.shader"))
        self._tool_handle_shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "default.shader"))
        self._gl = OpenGL.getInstance().getBindingsObject()
        self._scene = Application.getInstance().getController().getScene()

        self._renderer = Application.getInstance().getRenderer()

        self._selection_map = {}
        self._toolhandle_selection_map = {
            Color.dropLowBits(self._dropAlpha(ToolHandle.DisabledSelectionColor)): ToolHandle.NoAxis,
            Color.dropLowBits(self._dropAlpha(ToolHandle.XAxisSelectionColor)): ToolHandle.XAxis,
            Color.dropLowBits(self._dropAlpha(ToolHandle.YAxisSelectionColor)): ToolHandle.YAxis,
            Color.dropLowBits(self._dropAlpha(ToolHandle.ZAxisSelectionColor)): ToolHandle.ZAxis,
            Color.dropLowBits(self._dropAlpha(ToolHandle.AllAxisSelectionColor)): ToolHandle.AllAxis,
            Color.dropLowBits(ToolHandle.DisabledSelectionColor): ToolHandle.NoAxis,
            Color.dropLowBits(ToolHandle.XAxisSelectionColor): ToolHandle.XAxis,
            Color.dropLowBits(ToolHandle.YAxisSelectionColor): ToolHandle.YAxis,
            Color.dropLowBits(ToolHandle.ZAxisSelectionColor): ToolHandle.ZAxis,
            Color.dropLowBits(ToolHandle.AllAxisSelectionColor): ToolHandle.AllAxis
        }

        self._output = None

    ##  Perform the actual rendering.
    def render(self):
        self._selection_map = self._toolhandle_selection_map.copy()

        batch = RenderBatch(self._shader)
        tool_handle = RenderBatch(self._tool_handle_shader, type = RenderBatch.RenderType.Overlay)
        selectable_objects = False
        for node in DepthFirstIterator(self._scene.getRoot()):
            if isinstance(node, ToolHandle):
                tool_handle.addItem(node.getWorldTransformation(), mesh = node.getSelectionMesh())
                continue

            if node.isSelectable() and node.getMeshData():
                selectable_objects = True
                batch.addItem(transformation = node.getWorldTransformation(), mesh = node.getMeshData(), uniforms = { "selection_color": self._getNodeColor(node)})

        self.bind()
        if selectable_objects:
            batch.render(self._scene.getActiveCamera())

            self._gl.glColorMask(self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_FALSE)
            self._gl.glDisable(self._gl.GL_DEPTH_TEST)

            tool_handle.render(self._scene.getActiveCamera())

            self._gl.glEnable(self._gl.GL_DEPTH_TEST)
            self._gl.glColorMask(self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_TRUE, self._gl.GL_TRUE)

        self.release()

    ##  Get the object id at a certain pixel coordinate.
    def getIdAtPosition(self, x, y):
        output = self.getOutput()

        window_size = self._renderer.getWindowSize()

        px = (0.5 + x / 2.0) * window_size[0]
        py = (0.5 + y / 2.0) * window_size[1]

        if px < 0 or px > (output.width() - 1) or py < 0 or py > (output.height() - 1):
            return None

        pixel = output.pixel(px, py)
        return self._selection_map.get(Color.fromARGBHighBits(pixel), None)

    ## Get an unique identifier to the face of the polygon at a certain pixel-coordinate.
    def getFaceIdAtPosition(self, x, y):
        output = self.getOutput()

        window_size = self._renderer.getWindowSize()

        px = (0.5 + x / 2.0) * window_size[0]
        py = (0.5 + y / 2.0) * window_size[1]

        if px < 0 or px > (output.width() - 1) or py < 0 or py > (output.height() - 1):
            return -1

        face_color = Color.fromARGBLowBits(output.pixel(px, py))
        return (
            (int(face_color.a * 255.) << 12) |
            (int(face_color.b * 255.) << 8) |
            (int(face_color.g * 255.) << 4) |
            int(face_color.r * 255.)
        )

    def _getNodeColor(self, node):
        while True:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            a = 255 if Selection.isSelected(node) or self._isInSelectedGroup(node) else 0
            color = Color(r & 0xf0, g & 0xf0, b & 0xf0, a & 0xf0)

            if color not in self._selection_map:
                break

        self._selection_map[color] = id(node)

        return color

    def _dropAlpha(self, color):
        return Color(color.r, color.g, color.b, 0.0)

    ##  Get the top root group for a node
    #
    #   \param node type(SceneNode)
    #   \return group type(SceneNode)
    def _isInSelectedGroup(self, node):
        group_node = node.getParent()
        while group_node.callDecoration("isGroup"):
            if Selection.isSelected(group_node):
                return True
            group_node = group_node.getParent()
        return False