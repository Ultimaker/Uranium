from UM.Tool import Tool
from UM.Event import Event

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.ScaleOperation import ScaleOperation
from UM.Application import Application

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import MirrorToolHandle

class MirrorTool(Tool):
    def __init__(self):
        super().__init__()

        self._renderer = Application.getInstance().getRenderer()

        self._handle = MirrorToolHandle.MirrorToolHandle()

        self._locked_axis = None

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            if Selection.hasSelection():
                #TODO: Support multiple selection
                self._handle.setParent(self.getController().getScene().getRoot())
                self._handle.setPosition(Selection.getSelectedObject(0).getGlobalPosition())

        if event.type == Event.MousePressEvent:
            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return

            if ToolHandle.isAxis(id):
                self._locked_axis = id
                return True

        if event.type == Event.MouseMoveEvent:
            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not self._locked_axis:
                if not id:
                    self._handle.setActiveAxis(None)

                if ToolHandle.isAxis(id):
                    self._handle.setActiveAxis(id)

            return False

        if event.type == Event.MouseReleaseEvent:
            if self._locked_axis:
                for node in Selection.getAllSelectedObjects():
                    scale = node.getScale()
                    if self._locked_axis == ToolHandle.XAxis:
                        scale.setX(-scale.x)
                    elif self._locked_axis == ToolHandle.YAxis:
                        scale.setY(-scale.y)
                    elif self._locked_axis == ToolHandle.ZAxis:
                        scale.setZ(-scale.z)

                    op = ScaleOperation(node, scale, set_scale = True)
                    Application.getInstance().getOperationStack().push(op)

                self._locked_axis = None
                return True

        if event.type == Event.ToolDeactivateEvent:
            self._handle.setParent(None)

        return False
