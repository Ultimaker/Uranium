# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import time

from UM.Benchmark import Benchmark
from UM.Tool import Tool
from UM.Event import Event, MouseEvent, KeyEvent

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.TranslateOperation import TranslateOperation
from UM.Operations.GroupedOperation import GroupedOperation

from UM.Scene.SceneNodeSettings import SceneNodeSettings
from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from PyQt5.QtCore import Qt

from . import TranslateToolHandle


DIMENSION_TOLERANCE = 0.0001  # Tolerance value used for comparing dimensions from the UI.
DIRECTION_TOLERANCE = 0.0001  # Used to check if you're perpendicular on some axis

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

        self._shortcut_key = Qt.Key_T

        self._distance_update_time = None
        self._distance = None

        self.setExposedProperties("ToolHint",
                                  "X",
                                  "Y",
                                  "Z",
                                  SceneNodeSettings.LockPosition)

        # Ensure that the properties (X, Y & Z) are updated whenever the selection center is changed.
        Selection.selectionCenterChanged.connect(self.propertyChanged)


    ##  Get the x-location of the selection bounding box center
    #
    #   \param x type(float) location in mm
    def getX(self):
        if Selection.hasSelection():
            return float(Selection.getBoundingBox().center.x)
        return 0.0

    ##  Get the y-location of the selection bounding box center
    #
    #   \param y type(float) location in mm
    def getY(self):
        if Selection.hasSelection():
            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            return float(Selection.getBoundingBox().center.z)
        return 0.0

    ##  Get the z-location of the selection bounding box bottom
    #   The bottom is used as opposed to the center, because the biggest usecase is to push the selection into the buildplate
    #
    #   \param z type(float) location in mm
    def getZ(self):
        # We want to display based on the bottom instead of the actual coordinate.
        if Selection.hasSelection():
            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            return float(Selection.getBoundingBox().bottom)
        return 0.0

    def _parseInt(self, str_value):
        try:
            parsed_value = float(str_value)
        except ValueError:
            parsed_value = float(0)
        return parsed_value

    ##  Set the x-location of the selected object(s) by translating relative to the selection bounding box center
    #
    #   \param x type(float) location in mm
    def setX(self, x):
        Benchmark.start("Moving object in X from {start} to {end}".format(start = self.getX(), end = x))
        parsed_x = self._parseInt(x)
        bounding_box = Selection.getBoundingBox()

        op = GroupedOperation()
        if not Float.fuzzyCompare(parsed_x, float(bounding_box.center.x), DIMENSION_TOLERANCE):
            for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
                world_position = selected_node.getWorldPosition()
                new_position = world_position.set(x=parsed_x + (world_position.x - bounding_box.center.x))
                node_op = TranslateOperation(selected_node, new_position, set_position = True)
                op.addOperation(node_op)
            op.push()
        self._controller.toolOperationStopped.emit(self)

    ##  Set the y-location of the selected object(s) by translating relative to the selection bounding box center
    #
    #   \param y type(float) location in mm
    def setY(self, y):
        Benchmark.start("Moving object in Y from {start} to {end}".format(start = self.getY(), end = y))
        parsed_y = self._parseInt(y)
        bounding_box = Selection.getBoundingBox()

        op = GroupedOperation()
        if not Float.fuzzyCompare(parsed_y, float(bounding_box.center.z), DIMENSION_TOLERANCE):
            for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
                # Note; The switching of z & y is intentional. We display z as up for the user,
                # But store the data in openGL space.
                world_position = selected_node.getWorldPosition()
                new_position = world_position.set(z=parsed_y + (world_position.z - bounding_box.center.z))

                node_op = TranslateOperation(selected_node, new_position, set_position = True)
                op.addOperation(node_op)
            op.push()
        self._controller.toolOperationStopped.emit(self)

    ##  Set the y-location of the selected object(s) by translating relative to the selection bounding box bottom
    #
    #   \param z type(float) location in mm
    def setZ(self, z):
        Benchmark.start("Moving object in Z from {start} to {end}".format(start = self.getZ(), end = z))
        parsed_z = self._parseInt(z)
        bounding_box = Selection.getBoundingBox()

        op = GroupedOperation()
        if not Float.fuzzyCompare(parsed_z, float(bounding_box.bottom), DIMENSION_TOLERANCE):
            for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
                # Note: The switching of z & y is intentional. We display z as up for the user,
                # But store the data in openGL space.
                world_position = selected_node.getWorldPosition()
                new_position = world_position.set(y=parsed_z + (world_position.y - bounding_box.bottom))
                node_op = TranslateOperation(selected_node, new_position, set_position = True)
                op.addOperation(node_op)
            op.push()
        self._controller.toolOperationStopped.emit(self)

    ##  Set which axis/axes are enabled for the current translate operation
    #
    #   \param axis type(list) list of axes (expressed as ToolHandle enum)
    def setEnabledAxis(self, axis):
        self._enabled_axis = axis
        self._handle.setEnabledAxis(axis)


    ##  Set lock setting to the object. This setting will be used to prevent model movement on the build plate
    #
    #   \param value type(bool) the setting state
    def setLockPosition(self, value):
        for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
            selected_node.setSetting(SceneNodeSettings.LockPosition, value)

    def getLockPosition(self):
        total_size = Selection.getCount()
        false_state_counter = 0
        true_state_counter = 0
        if Selection.hasSelection():
            for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():

                if selected_node.getSetting(SceneNodeSettings.LockPosition, False):
                    true_state_counter += 1
                else:
                    false_state_counter +=1

            if  total_size == false_state_counter: # if no locked positions
                return False
            elif total_size == true_state_counter: # if all selected objects are locked
                return True
            else:
                return "partially"  # if at least one is locked


        return False

    ##  Handle mouse and keyboard events
    #
    #   \param event type(Event)
    def event(self, event):
        super().event(event)

        # Make sure the displayed values are updated if the bounding box of the selected mesh(es) changes
        if event.type == Event.ToolActivateEvent:
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                node.boundingBoxChanged.connect(self.propertyChanged)

        if event.type == Event.ToolDeactivateEvent:
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                node.boundingBoxChanged.disconnect(self.propertyChanged)

        if event.type == Event.KeyPressEvent and event.key == KeyEvent.ShiftKey:
            return False


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

            camera_direction = self._controller.getScene().getActiveCamera().getPosition().normalized()

            abs_x = abs(camera_direction.x)
            abs_y = abs(camera_direction.y)

            # We have to define a plane vector that is suitable for the selected toolhandle axis
            # and at the same time the camera direction should not be exactly perpendicular to the plane vector
            if id == ToolHandle.XAxis:
                plane_vector = Vector(0, camera_direction.y, camera_direction.z).normalized()
            elif id == ToolHandle.YAxis:
                plane_vector = Vector(camera_direction.x, 0, camera_direction.z).normalized()
            elif id == ToolHandle.ZAxis:
                plane_vector = Vector(camera_direction.x, camera_direction.y, 0).normalized()
            else:
                if abs_y > DIRECTION_TOLERANCE:
                    plane_vector = Vector(0, 1, 0)
                elif abs_x > DIRECTION_TOLERANCE:
                    plane_vector = Vector(1, 0, 0)
                    self.setLockedAxis(ToolHandle.ZAxis)  # Do not move y / vertical
                else:
                    plane_vector = Vector(0, 0, 1)
                    self.setLockedAxis(ToolHandle.XAxis)  # Do not move y / vertical

            self.setDragPlane(Plane(plane_vector, 0))

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
                    drag = drag.set(y=0, z=0)
                elif self.getLockedAxis() == ToolHandle.YAxis:
                    drag = drag.set(x=0, z=0)
                elif self.getLockedAxis() == ToolHandle.ZAxis:
                    drag = drag.set(x=0, y=0)

                if not self._moved:
                    self._moved = True
                    self._distance = Vector(0, 0, 0)
                    self.operationStarted.emit(self)

                op = GroupedOperation()
                for node in self._getSelectedObjectsWithoutSelectedAncestors():
                    if not node.getSetting(SceneNodeSettings.LockPosition, False):
                        op.addOperation(TranslateOperation(node, drag))

                op.push()

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
                self.setLockedAxis(ToolHandle.NoAxis)
                self.setDragPlane(None)
                self.setDragStart(None, None)
                return True

        return False

    ##  Return a formatted distance of the current translate operation
    #
    #   \return type(String) fully formatted string showing the distance by which the mesh(es) are dragged
    def getToolHint(self):
        return "%.2f mm" % self._distance.length() if self._distance else None
