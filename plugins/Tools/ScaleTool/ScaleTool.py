# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import List, Tuple, TYPE_CHECKING, Optional

from PyQt5.QtCore import Qt

from UM.Event import Event, MouseEvent, KeyEvent
from UM.Math.Float import Float
from UM.Math.Matrix import Matrix
from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.ScaleOperation import ScaleOperation
from UM.Operations.SetTransformOperation import SetTransformOperation
from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool

try:
    from . import ScaleToolHandle
except (ImportError, SystemError):
    import ScaleToolHandle  # type: ignore  # This fixes the tests not being able to import.

import scipy
if TYPE_CHECKING:
    from UM.Scene.SceneNode import SceneNode

DIMENSION_TOLERANCE = 0.0001    # Tolerance value used for comparing dimensions from the UI.


class ScaleTool(Tool):
    """Provides the tool to scale meshes and groups"""

    def __init__(self):
        super().__init__()
        self._handle = ScaleToolHandle.ScaleToolHandle()

        self._snap_scale = False
        self._non_uniform_scale = False
        self._scale_speed = 10

        self._drag_length = 0

        self._move_up = True

        self._shortcut_key = Qt.Key_S

        # We use the position of the scale handle when the operation starts.
        # This is done in order to prevent runaway reactions (drag changes of 100+)
        self._saved_handle_position = None  # for non uniform drag
        self._scale_sum = 0.0  # a memory for uniform drag with snap scaling
        self._last_event = None  # type: Optional[Event] # for uniform drag

        self._saved_node_positions = []  # type: List[Tuple[SceneNode, Vector]]

        self.setExposedProperties(
            "ScaleSnap",
            "NonUniformScale",
            "ObjectWidth",
            "ObjectHeight",
            "ObjectDepth",
            "ScaleX",
            "ScaleY",
            "ScaleZ"
        )

    def event(self, event):
        """Handle mouse and keyboard events

        :param event: type(Event)
        """

        super().event(event)

        if event.type == Event.ToolActivateEvent:
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                node.boundingBoxChanged.connect(self.propertyChanged)

        if event.type == Event.ToolDeactivateEvent:
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                node.boundingBoxChanged.disconnect(self.propertyChanged)

        # Handle modifier keys: Shift toggles snap, Control toggles uniform scaling
        if event.type == Event.KeyPressEvent:
            if event.key == KeyEvent.ShiftKey:
                self.setScaleSnap(not self._snap_scale)

            elif event.key == KeyEvent.ControlKey:
                self.setNonUniformScale(not self._non_uniform_scale)

        if event.type == Event.KeyReleaseEvent:
            if event.key == KeyEvent.ShiftKey:
                self.setScaleSnap(not self._snap_scale)

            elif event.key == KeyEvent.ControlKey:
                self.setNonUniformScale(not self._non_uniform_scale)

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            # Initialise a scale operation
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._selection_pass.getIdAtPosition(event.x, event.y)
            if not id:
                return False

            if self._handle.isAxis(id):
                self.setLockedAxis(id)
            self._saved_handle_position = self._handle.getWorldPosition()

            # Save the current positions of the node, as we want to scale arround their current centres
            self._saved_node_positions = []
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                self._saved_node_positions.append((node, node.getPosition()))

            self._scale_sum = 0.0
            self._last_event = event

            if id == ToolHandle.XAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), self._saved_handle_position.z))
            elif id == ToolHandle.YAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), self._saved_handle_position.z))
            elif id == ToolHandle.ZAxis:
                self.setDragPlane(Plane(Vector(0, 1, 0), self._saved_handle_position.y))
            else:
                self.setDragPlane(Plane(Vector(0, 1, 0), self._saved_handle_position.y))

            self.setDragStart(event.x, event.y)
            return True

        if event.type == Event.MouseMoveEvent:
            # Perform a scale operation
            if not self.getDragPlane():
                return False

            drag_position = self.getDragPosition(event.x, event.y)
            if drag_position:
                if self.getLockedAxis() == ToolHandle.XAxis:
                    drag_position = drag_position.set(y = 0, z = 0)
                elif self.getLockedAxis() == ToolHandle.YAxis:
                    drag_position = drag_position.set(x = 0, z = 0)
                elif self.getLockedAxis() == ToolHandle.ZAxis:
                    drag_position = drag_position.set(x = 0, y = 0)

                drag_length = (drag_position - self._saved_handle_position).length()
                if self._drag_length > 0:
                    drag_change = (drag_length - self._drag_length) / 100 * self._scale_speed
                    if self.getLockedAxis() in [ToolHandle.XAxis, ToolHandle.YAxis, ToolHandle.ZAxis]:
                        # drag the handle, axis is already determined
                        if self._snap_scale:
                            scale_factor = round(drag_change, 1)
                        else:
                            scale_factor = drag_change
                    else:
                        # uniform scaling; because we use central cube, we use the screen x, y for scaling.
                        # upper right is scale up, lower left is scale down
                        scale_factor_delta = ((self._last_event.y - event.y) - (self._last_event.x - event.x)) * self._scale_speed
                        self._scale_sum += scale_factor_delta
                        if self._snap_scale:
                            scale_factor = round(self._scale_sum, 1)
                            # remember the decimals when snap scaling
                            self._scale_sum -= scale_factor
                        else:
                            scale_factor = self._scale_sum
                            self._scale_sum = 0.0
                    if scale_factor:
                        scale_change = Vector(0.0, 0.0, 0.0)
                        if self._non_uniform_scale:
                            if self.getLockedAxis() == ToolHandle.XAxis:
                                scale_change = scale_change.set(x=scale_factor)
                            elif self.getLockedAxis() == ToolHandle.YAxis:
                                scale_change = scale_change.set(y=scale_factor)
                            elif self.getLockedAxis() == ToolHandle.ZAxis:
                                scale_change = scale_change.set(z=scale_factor)
                            else:
                                # Middle handle
                                scale_change = scale_change.set(x=scale_factor, y=scale_factor, z=scale_factor)
                        else:
                            scale_change = scale_change.set(x=scale_factor, y=scale_factor, z=scale_factor)

                        # Scale around the saved centers of all selected nodes
                        if len(self._saved_node_positions) > 1:
                            op = GroupedOperation()
                            for node, position in self._saved_node_positions:
                                op.addOperation(ScaleOperation(node, scale_change, relative_scale = True, scale_around_point = position))
                            op.push()
                        else:
                            for node, position in self._saved_node_positions:
                                ScaleOperation(node, scale_change, relative_scale = True, scale_around_point = position).push()
                        self._drag_length = (self._saved_handle_position - drag_position).length()
                else:
                    self.operationStarted.emit(self)
                    self._drag_length = (self._saved_handle_position - drag_position).length() #First move, do nothing but set right length.
                self._last_event = event  # remember for uniform drag
                return True

        if event.type == Event.MouseReleaseEvent:
            # Finish a scale operation
            if self.getDragPlane():
                self.setDragPlane(None)
                self.setLockedAxis(ToolHandle.NoAxis)
                self._drag_length = 0
                self.operationStopped.emit(self)
                return True

    def resetScale(self):
        """Reset scale of the selected objects"""

        Selection.applyOperation(SetTransformOperation, None, None, Vector(1.0, 1.0, 1.0), Vector(0, 0, 0))

    def getNonUniformScale(self):
        """Get non-uniform scaling flag

        :return: scale type(boolean)
        """

        return self._non_uniform_scale

    def setNonUniformScale(self, scale):
        """Set non-uniform scaling flag

        :param scale: type(boolean)
        """

        if scale != self._non_uniform_scale:
            self._non_uniform_scale = scale
            self.propertyChanged.emit()

    def getScaleSnap(self):
        """Get snap scaling flag

        :return: snap type(boolean)
        """

        return self._snap_scale

    def setScaleSnap(self, snap):
        """Set snap scaling flag

        :param snap: type(boolean)
        """

        if self._snap_scale != snap:
            self._snap_scale = snap
            self.propertyChanged.emit()

    def getObjectWidth(self) -> float:
        """Get the width of the bounding box of the selected object(s)

        :return: width Width in mm.
        """

        selection = Selection.getSelectedObject(0)
        if selection:
            aabb = selection.getBoundingBox()
            if aabb:
                return float(aabb.width)

        return 0.0

    def getObjectHeight(self) -> float:
        """Get the height of the bounding box of the selected object(s)

        :return: height Height in mm.
        """

        selection = Selection.getSelectedObject(0)
        if selection:
            aabb = selection.getBoundingBox()
            if aabb:
                return float(aabb.height)

        return 0.0

    def getObjectDepth(self) -> float:
        """Get the depth of the bounding box of the first selected object

        :return: depth Depth in mm.
        """

        selection = Selection.getSelectedObject(0)
        if selection:
            aabb = selection.getBoundingBox()
            if aabb:
                return float(aabb.depth)

        return 0.0

    def getScaleX(self):
        """Get the x-axis scale of the first selected object

        :return: scale type(float) scale factor (1.0 = normal scale)
        """

        if Selection.hasSelection():
            ## Ensure that the returned value is positive (mirror causes scale to be negative)
            return abs(round(float(self._getScaleInWorldCoordinates(Selection.getSelectedObject(0)).x), 4))

        return 1.0

    def getScaleY(self):
        """Get the y-axis scale of the first selected object

        :return: scale type(float) scale factor (1.0 = normal scale)
        """

        if Selection.hasSelection():
            ## Ensure that the returned value is positive (mirror causes scale to be negative)
            return abs(round(float(self._getScaleInWorldCoordinates(Selection.getSelectedObject(0)).y), 4))

        return 1.0

    def getScaleZ(self):
        """Get the z-axis scale of the of the first selected object

        :return: scale type(float) scale factor (1.0 = normal scale)
        """

        if Selection.hasSelection():
            ## Ensure that the returned value is positive (mirror causes scale to be negative)
            return abs(round(float(self._getScaleInWorldCoordinates(Selection.getSelectedObject(0)).z), 4))

        return 1.0

    def setObjectWidth(self, width):
        """Set the width of the selected object(s) by scaling the first selected object to a certain width

        :param width: type(float) width in mm
        """

        obj = Selection.getSelectedObject(0)
        if obj:
            width = float(width)
            obj_width = obj.getBoundingBox().width
            if not Float.fuzzyCompare(obj_width, width, DIMENSION_TOLERANCE):
                scale_factor = width / obj_width
                if self._non_uniform_scale:
                    scale_vector = Vector(scale_factor, 1, 1)
                else:
                    scale_vector = Vector(scale_factor, scale_factor, scale_factor)

                self._scaleSelectedNodes(scale_vector)
    def setObjectHeight(self, height):
        """Set the height of the selected object(s) by scaling the first selected object to a certain height

        :param height: type(float) height in mm
        """

        obj = Selection.getSelectedObject(0)
        if obj:
            height = float(height)
            obj_height = obj.getBoundingBox().height
            if not Float.fuzzyCompare(obj_height, height, DIMENSION_TOLERANCE):
                scale_factor = height / obj_height
                if self._non_uniform_scale:
                    scale_vector = Vector(1, scale_factor, 1)
                else:
                    scale_vector = Vector(scale_factor, scale_factor, scale_factor)

                self._scaleSelectedNodes(scale_vector)

    def setObjectDepth(self, depth):
        """Set the depth of the selected object(s) by scaling the first selected object to a certain depth

        :param depth: type(float) depth in mm
        """

        obj = Selection.getSelectedObject(0)
        if obj:
            depth = float(depth)
            obj_depth = obj.getBoundingBox().depth
            if not Float.fuzzyCompare(obj_depth, depth, DIMENSION_TOLERANCE):
                scale_factor = depth / obj_depth
                if self._non_uniform_scale:
                    scale_vector = Vector(1, 1, scale_factor)
                else:
                    scale_vector = Vector(scale_factor, scale_factor, scale_factor)

                self._scaleSelectedNodes(scale_vector)

    def setScaleX(self, scale):
        """Set the x-scale of the selected object(s) by scaling the first selected object to a certain factor

        :param scale: type(float) scale factor (1.0 = normal scale)
        """

        obj = Selection.getSelectedObject(0)
        if obj:
            obj_scale = self._getScaleInWorldCoordinates(obj)
            if round(float(obj_scale.x), 4) != scale:
                scale_factor = abs(scale / obj_scale.x)
                if self._non_uniform_scale:
                    scale_vector = Vector(scale_factor, 1, 1)
                else:
                    scale_vector = Vector(scale_factor, scale_factor, scale_factor)

                self._scaleSelectedNodes(scale_vector)

    def setScaleY(self, scale):
        """Set the y-scale of the selected object(s) by scaling the first selected object to a certain factor

        :param scale: type(float) scale factor (1.0 = normal scale)
        """

        obj = Selection.getSelectedObject(0)
        if obj:
            obj_scale = self._getScaleInWorldCoordinates(obj)
            if round(float(obj_scale.y), 4) != scale:
                scale_factor = abs(scale / obj_scale.y)
                if self._non_uniform_scale:
                    scale_vector = Vector(1, scale_factor, 1)
                else:
                    scale_vector = Vector(scale_factor, scale_factor, scale_factor)

                self._scaleSelectedNodes(scale_vector)

    def setScaleZ(self, scale):
        """Set the z-scale of the selected object(s) by scaling the first selected object to a certain factor

        :param scale: type(float) scale factor (1.0 = normal scale)
        """

        obj = Selection.getSelectedObject(0)
        if obj:
            obj_scale = self._getScaleInWorldCoordinates(obj)
            if round(float(obj_scale.z), 4) != scale:
                scale_factor = abs(scale / obj_scale.z)
                if self._non_uniform_scale:
                    scale_vector = Vector(1, 1, scale_factor)
                else:
                    scale_vector = Vector(scale_factor, scale_factor, scale_factor)

                self._scaleSelectedNodes(scale_vector)

    def _scaleSelectedNodes(self, scale_vector: Vector) -> None:
        selected_nodes = self._getSelectedObjectsWithoutSelectedAncestors()
        if len(selected_nodes) > 1:
            op = GroupedOperation()
            for node in selected_nodes:
                op.addOperation(ScaleOperation(node, scale_vector, scale_around_point=node.getWorldPosition()))
            op.push()
        else:
            for node in selected_nodes:
                ScaleOperation(node, scale_vector, scale_around_point=node.getWorldPosition()).push()

    def _getScaleInWorldCoordinates(self, node):
        """Convenience function that gives the scale of an object in the coordinate space of the world.

        The function might return wrong value if the grouped models are rotated

        :param node: type(SceneNode)
        :return: scale type(float) scale factor (1.0 = normal scale)
        """
        aabb = node.getBoundingBox()
        original_aabb = self._getRotatedExtents(node)
        if aabb is not None and original_aabb is not None:
            scale = Vector(aabb.width / original_aabb.width, aabb.height / original_aabb.height,
                           aabb.depth / original_aabb.depth)
            return scale
        else:
            return Vector(1, 1, 1)

    def _getSVDRotationFromMatrix(self, matrix):
        result = Matrix()
        rotation_data = matrix.getData()[:3, :3]
        U, s, Vh = scipy.linalg.svd(rotation_data)
        result._data[:3, :3] = U.dot(Vh)
        return result

    def _getExtents(self, node, matrix):
        extents = None
        modified_matrix = matrix.multiply(node.getLocalTransformation(), copy = True)
        if node.getMeshData():
            extents = node.getMeshData().getExtents(modified_matrix)

        for child in node.getChildren():
            if extents is None:
                extents = self._getExtents(child, modified_matrix)
            else:
                extents = extents + self._getExtents(child, modified_matrix)
        return extents

    def _getRotatedExtents(self, node, with_translation = False):
        # The rotation matrix that we get back from our own decompose isn't quite correct for some reason.
        # It seems that it does not "draw the line" between scale, rotate & skew quite correctly in all cases.
        # The decomposition is insanely fast and the combination of all of the components does result in the same
        # Transformation matrix (Also note that there are multiple solutions for decomposition and that one just doesn't
        # work here, but fine everywhere else).
        #
        # In order to remedy this, we use singular value decomposition.
        # SVD solves a = U s V.H for us, where A is the matrix. U and V.h are Rotation matrices and s holds the scale.
        extents = None
        rotated_matrix = self._getSVDRotationFromMatrix(node.getWorldTransformation())
        if node.getMeshData():
            if with_translation:
                rotated_matrix._data[:3, 3] = node.getPosition().getData()

            extents = node.getMeshData().getExtents(rotated_matrix)
        if node.callDecoration("isGroup"):
            for child in node.getChildren():
                # We want the children with their (local) translation, as this influences the size of the AABB.
                if extents is None:
                    extents = self._getExtents(child, rotated_matrix)
                else:
                    extents = extents + self._getExtents(child, rotated_matrix)
        return extents