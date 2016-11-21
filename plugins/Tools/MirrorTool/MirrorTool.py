# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent

from UM.Math.Vector import Vector

from UM.Operations.MirrorOperation import MirrorOperation
from UM.Operations.GroupedOperation import GroupedOperation

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import MirrorToolHandle

##  Provides the tool to mirror meshes and groups

class MirrorTool(Tool):
    def __init__(self):
        super().__init__()

        self._handle = MirrorToolHandle.MirrorToolHandle()

        self._operation_started = False

    ##  Handle mouse and keyboard events
    #
    #   \param event type(Event)
    def event(self, event):
        super().event(event)

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            # Initialise a mirror operation
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._selection_pass.getIdAtPosition(event.x, event.y)
            if not id:
                return False

            if ToolHandle.isAxis(id):
                self.setLockedAxis(id)
                self._operation_started = True
                self.operationStarted.emit(self)
                return True

        if event.type == Event.MouseReleaseEvent:
            if self._operation_started:
                self._operation_started = False
                self.operationStopped.emit(self)

            # Perform a mirror operation
            if self.getLockedAxis():
                op = None
                if Selection.getCount() == 1:
                    node = Selection.getSelectedObject(0)
                    if self.getLockedAxis() == ToolHandle.XAxis:
                        mirror = Vector(-1, 1, 1)
                    elif self.getLockedAxis() == ToolHandle.YAxis:
                        mirror = Vector(1, -1, 1)
                    elif self.getLockedAxis() == ToolHandle.ZAxis:
                        mirror = Vector(1, 1, -1)
                    else:
                        mirror = Vector(1, 1, 1)
                    op = MirrorOperation(node, mirror, mirror_around_center = True)
                else:
                    op = GroupedOperation()

                    for node in Selection.getAllSelectedObjects():
                        if self.getLockedAxis() == ToolHandle.XAxis:
                            mirror = Vector(-1, 1, 1)
                        elif self.getLockedAxis() == ToolHandle.YAxis:
                            mirror = Vector(1, -1, 1)
                        elif self.getLockedAxis() == ToolHandle.ZAxis:
                            mirror = Vector(1, 1, -1)
                        else:
                            mirror = Vector(1, 1, 1)

                        op.addOperation(MirrorOperation(node, mirror, mirror_around_center = True))

                op.push()

                self.setLockedAxis(None)
                return True

        return False
