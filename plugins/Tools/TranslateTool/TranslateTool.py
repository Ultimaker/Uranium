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

import time

##  Provides the tool to move meshes and groups
#
#   The tool exposes a ToolHint to show the distance of the current operation

class TranslateTool(Tool):
    def __init__(self):
        super().__init__()

        self._handle = TranslateToolHandle.TranslateToolHandle()
        self._enabled_axis = [ToolHandle.XAxis, ToolHandle.YAxis, ToolHandle.ZAxis]

        self._grid_snap = False
        self._grid_size = 10
        self._moved = False

        self._distance_update_time = None
        self._distance = None

        self.setExposedProperties("ToolHint", "X", "Y", "Z")

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
        # We want to display based on the bottom instead of the actual coordinate.
        if Selection.hasSelection():
            selected_node = Selection.getSelectedObject(0)
            try:
                bottom = selected_node.getBoundingBox().bottom
            except AttributeError: #It can happen that there is no bounding box yet.
                bottom = 0

            return float(bottom)
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
            center = selected_node.getBoundingBox().center
            bottom = selected_node.getBoundingBox().bottom
            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.

            new_position.setY(float(z) + (center.y - bottom))
            Selection.applyOperation(TranslateOperation, new_position, set_position = True)
            self.operationStopped.emit(self)

    ##  Set which axis/axes are enabled for the current translate operation
    #
    #   \param axis type(list) list of axes (expressed as ToolHandle enum)
    def setEnabledAxis(self, axis):
        self._enabled_axis = axis
        self._handle.setEnabledAxis(axis)

    ##  Handle mouse and keyboard events
    #
    #   \param event type(Event)
    def event(self, event):
        super().event(event)

        # Make sure the displayed values are updated if the boundingbox of the selected mesh(es) changes
        if event.type == Event.ToolActivateEvent:
            for node in Selection.getAllSelectedObjects():
                node.boundingBoxChanged.connect(self.propertyChanged)

        if event.type == Event.ToolDeactivateEvent:
            for node in Selection.getAllSelectedObjects():
                node.boundingBoxChanged.disconnect(self.propertyChanged)

        if event.type == Event.KeyPressEvent and event.key == KeyEvent.ShiftKey:
            # Snap-to-grid is turned on when pressing the shift button
            self._grid_snap = True

        if event.type == Event.KeyReleaseEvent and event.key == KeyEvent.ShiftKey:
            # Snap-to-grid is turned off when releasing the shift button
            self._grid_snap = False

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            # Start a translate operation

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
            # Perform a translate operation

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
                    self._distance = Vector(0, 0, 0)
                    self.operationStarted.emit(self)

                Selection.applyOperation(TranslateOperation, drag)
                self._distance += drag

            self.setDragStart(event.x, event.y)

            # Rate-limit the angle change notification
            # This is done to prevent the UI from being flooded with property change notifications,
            # which in turn would trigger constant repaints.
            new_time = time.monotonic()
            if not self._distance_update_time or new_time - self._distance_update_time > 0.1:
                self.propertyChanged.emit()
                self._distance_update_time = new_time

            return True

        if event.type == Event.MouseReleaseEvent:
            # Finish a translate operation
            if self.getDragPlane():
                self.operationStopped.emit(self)
                self._distance = None
                self.propertyChanged.emit()
                # Force scene changed event. Some plugins choose to ignore move events when operation is in progress.
                if self._moved:
                    for node in Selection.getAllSelectedObjects():
                        Application.getInstance().getController().getScene().sceneChanged.emit(node)
                    self._moved = False
                self.setLockedAxis(None)
                self.setDragPlane(None)
                self.setDragStart(None, None)
                return True

        return False

    ##  Return a formatted distance of the current translate operation
    #
    #   \return type(String) fully formatted string showing the distance by which the mesh(es) are dragged
    def getToolHint(self):
        return "%.2f mm" % self._distance.length() if self._distance else None