# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent, KeyEvent

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.TranslateOperation import TranslateOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Application import Application

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import TranslateToolHandle

class TranslateTool(Tool):
    def __init__(self):
        super().__init__()

        self._handle = TranslateToolHandle.TranslateToolHandle()
        self._enabled_axis = [ToolHandle.XAxis, ToolHandle.YAxis, ToolHandle.ZAxis]

        self._grid_snap = False
        self._grid_size = 10
        self._moved = False
        self.setExposedProperties(
            "X",
            "Y",
            "Z"
        )

    def getX(self):
        if Selection.hasSelection():
            return float(Selection.getSelectedObject(0).getWorldPosition().x)
        return 0.0

    def getY(self):
        if Selection.hasSelection():
            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            return float(Selection.getSelectedObject(0).getWorldPosition().z)
        return 0.0

    def getZ(self):
        if Selection.hasSelection():
            selected_node = Selection.getSelectedObject(0)
            center = selected_node.getMeshData().getCenterPosition()

            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            return float(Selection.getSelectedObject(0).getWorldPosition().y - center.y)
        return 0.0

    def setX(self, x):
        obj = Selection.getSelectedObject(0)
        if obj:
            new_position = obj.getWorldPosition()
            new_position.setX(x)
            Selection.applyOperation(TranslateOperation, new_position, set_position = True)
            self.operationStopped.emit(self)

    def setY(self, y):
        obj = Selection.getSelectedObject(0)
        if obj:
            new_position = obj.getWorldPosition()

            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            new_position.setZ(y)
            Selection.applyOperation(TranslateOperation, new_position, set_position = True)
            self.operationStopped.emit(self)

    def setZ(self, z):
        obj = Selection.getSelectedObject(0)
        if obj:
            new_position = obj.getWorldPosition()
            selected_node = Selection.getSelectedObject(0)
            center = selected_node.getMeshData().getCenterPosition()

            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            new_position.setY(float(z) + center.y)
            Selection.applyOperation(TranslateOperation, new_position, set_position = True)
            self.operationStopped.emit(self)

    def setEnabledAxis(self, axis):
        self._enabled_axis = axis
        self._handle.setEnabledAxis(axis)

    def event(self, event):
        super().event(event)

        if event.type == Event.ToolActivateEvent:
            for node in Selection.getAllSelectedObjects():
                node.boundingBoxChanged.connect(self.propertyChanged)

        if event.type == Event.ToolDeactivateEvent:
            for node in Selection.getAllSelectedObjects():
                node.boundingBoxChanged.disconnect(self.propertyChanged)

        if event.type == Event.KeyPressEvent and event.key == KeyEvent.ShiftKey:
            self._grid_snap = True

        if event.type == Event.KeyReleaseEvent and event.key == KeyEvent.ShiftKey:
            self._grid_snap = False

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._selection_pass.getIdAtPosition(event.x, event.y)
            if not id:
                return False

            if id in self._enabled_axis:
                self.setLockedAxis(id)
            elif self._handle.isAxis(id):
                return False

            self._moved = False
            if id == ToolHandle.XAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), 0))
            elif id == ToolHandle.YAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), 0))
            elif id == ToolHandle.ZAxis:
                self.setDragPlane(Plane(Vector(0, 1, 0), 0))
            else:
                self.setDragPlane(Plane(Vector(0, 1, 0), 0))

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            if not self.getDragStart():
                self.setDragStart(event.x, event.y)
                return False

            drag = self.getDragVector(event.x, event.y)
            if drag:
                if self._grid_snap and drag.length() < self._grid_size:
                    return False

                if self.getLockedAxis() == ToolHandle.XAxis:
                    drag.setY(0)
                    drag.setZ(0)
                elif self.getLockedAxis() == ToolHandle.YAxis:
                    drag.setX(0)
                    drag.setZ(0)
                elif self.getLockedAxis() == ToolHandle.ZAxis:
                    drag.setX(0)
                    drag.setY(0)

                if not self._moved:
                    self._moved = True
                    self.operationStarted.emit(self)

                Selection.applyOperation(TranslateOperation, drag)

            self.setDragStart(event.x, event.y)
            return True

        if event.type == Event.MouseReleaseEvent:
            if self.getDragPlane():
                self.operationStopped.emit(self)

                self.setLockedAxis(None)
                self.setDragPlane(None)
                self.setDragStart(None, None)
                return True

        return False
