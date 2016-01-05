# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.MirrorOperation import MirrorOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Application import Application

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import MirrorToolHandle

class MirrorTool(Tool):
    def __init__(self):
        super().__init__()

        self._handle = MirrorToolHandle.MirrorToolHandle()

    def event(self, event):
        super().event(event)

        if event.type == Event.MousePressEvent:
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._selection_pass.getIdAtPosition(event.x, event.y)
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
                    mirror = node.getMirror()
                    if self.getLockedAxis() == ToolHandle.XAxis:
                        mirror.setX(-mirror.x)
                    elif self.getLockedAxis() == ToolHandle.YAxis:
                        mirror.setY(-mirror.y)
                    elif self.getLockedAxis() == ToolHandle.ZAxis:
                        mirror.setZ(-mirror.z)

                    op = MirrorOperation(node, mirror, set_mirror=True)
                else:
                    op = GroupedOperation()

                    for node in Selection.getAllSelectedObjects():
                        mirror = node.getMirror()
                        if self.getLockedAxis() == ToolHandle.XAxis:
                            mirror.setX(-mirror.x)
                        elif self.getLockedAxis() == ToolHandle.YAxis:
                            mirror.setY(-mirror.y)
                        elif self.getLockedAxis() == ToolHandle.ZAxis:
                            mirror.setZ(-mirror.z)

                        op.addOperation(MirrorOperation(node, mirror, set_mirror = True))

                op.push()

                self.setLockedAxis(None)
                return True

        return False
