# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.ScaleOperation import ScaleOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Application import Application

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import MirrorToolHandle

class MirrorTool(Tool):
    def __init__(self):
        super().__init__()

        self._renderer = Application.getInstance().getRenderer()
        self._handle = MirrorToolHandle.MirrorToolHandle()

    def event(self, event):
        super().event(event)

        if event.type == Event.MousePressEvent:
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return False

            if ToolHandle.isAxis(id):
                self.setLockedAxis(id)
                return True

        if event.type == Event.MouseReleaseEvent:
            if self.getLockedAxis():
                op = None
                if Selection.getCount() == 1:
                    node = Selection.getSelectedObject(0)
                    scale = node.getScale()
                    if self.getLockedAxis() == ToolHandle.XAxis:
                        scale.setX(-scale.x)
                    elif self.getLockedAxis() == ToolHandle.YAxis:
                        scale.setY(-scale.y)
                    elif self.getLockedAxis() == ToolHandle.ZAxis:
                        scale.setZ(-scale.z)

                    op = ScaleOperation(node, scale, set_scale=True)
                else:
                    op = GroupedOperation()

                    for node in Selection.getAllSelectedObjects():
                        scale = node.getScale()
                        if self.getLockedAxis() == ToolHandle.XAxis:
                            scale.setX(-scale.x)
                        elif self.getLockedAxis() == ToolHandle.YAxis:
                            scale.setY(-scale.y)
                        elif self.getLockedAxis() == ToolHandle.ZAxis:
                            scale.setZ(-scale.z)

                        op.addOperation(ScaleOperation(node, scale, set_scale = True))

                op.push()

                self.setLockedAxis(None)
                return True

        return False
