# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional

from UM.Scene.SceneNode import SceneNode
from UM.Tool import Tool
from UM.Job import Job
from UM.Event import Event, MouseEvent, KeyEvent
from UM.Message import Message
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion

from PyQt5.QtCore import Qt

from UM.Operations.RotateOperation import RotateOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.SetTransformOperation import SetTransformOperation
from UM.Operations.LayFlatOperation import LayFlatOperation

from UM.Version import Version

from UM.View.GL.OpenGL import OpenGL
try:
    from . import RotateToolHandle
except (ImportError, SystemError):
    import RotateToolHandle  # type: ignore  # This fixes the tests not being able to import.

import math
import time

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")


##  Provides the tool to rotate meshes and groups
#
#   The tool exposes a ToolHint to show the rotation angle of the current operation
class RotateTool(Tool):
    def __init__(self):
        super().__init__()
        self._handle = RotateToolHandle.RotateToolHandle()

        self._snap_rotation = True
        self._snap_angle = math.radians(15)

        self._angle = None
        self._angle_update_time = None

        self._shortcut_key = Qt.Key_R

        self._progress_message = None
        self._iterations = 0
        self._total_iterations = 0
        self._rotating = False
        self.setExposedProperties("ToolHint", "RotationSnap", "RotationSnapAngle", "SelectFaceSupported", "SelectFaceToLayFlatMode")
        self._saved_node_positions = []

        self._select_face_mode = False
        Selection.selectedFaceChanged.connect(self._onSelectedFaceChanged)

    ##  Handle mouse and keyboard events
    #
    #   \param event type(Event)
    def event(self, event):
        super().event(event)

        if event.type == Event.KeyPressEvent and event.key == KeyEvent.ShiftKey:
            # Snap is toggled when pressing the shift button
            self.setRotationSnap(not self._snap_rotation)

        if event.type == Event.KeyReleaseEvent and event.key == KeyEvent.ShiftKey:
            # Snap is "toggled back" when releasing the shift button
            self.setRotationSnap(not self._snap_rotation)

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            # Start a rotate operation
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._selection_pass.getIdAtPosition(event.x, event.y)
            if not id:
                return False

            if self._handle.isAxis(id):
                self.setLockedAxis(id)
            else:
                # Not clicked on an axis: do nothing.
                return False

            handle_position = self._handle.getWorldPosition()

            # Save the current positions of the node, as we want to rotate around their current centres
            self._saved_node_positions = []
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                self._saved_node_positions.append((node, node.getPosition()))

            if id == ToolHandle.XAxis:
                self.setDragPlane(Plane(Vector(1, 0, 0), handle_position.x))
            elif id == ToolHandle.YAxis:
                self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))
            elif self._locked_axis == ToolHandle.ZAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), handle_position.z))
            else:
                self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))

            self.setDragStart(event.x, event.y)
            self._rotating = False
            self._angle = 0
            return True

        if event.type == Event.MouseMoveEvent:
            # Perform a rotate operation
            if not self.getDragPlane():
                return False

            if not self.getDragStart():
                self.setDragStart(event.x, event.y)
                if not self.getDragStart(): #May have set it to None.
                    return False

            if not self._rotating:
                self._rotating = True
                self.operationStarted.emit(self)

            handle_position = self._handle.getWorldPosition()

            drag_start = (self.getDragStart() - handle_position).normalized()
            drag_position = self.getDragPosition(event.x, event.y)
            if not drag_position:
                return False
            drag_end = (drag_position - handle_position).normalized()

            try:
                angle = math.acos(drag_start.dot(drag_end))
            except ValueError:
                angle = 0

            if self._snap_rotation:
                angle = int(angle / self._snap_angle) * self._snap_angle
                if angle == 0:
                    return False

            rotation = None
            if self.getLockedAxis() == ToolHandle.XAxis:
                direction = 1 if Vector.Unit_X.dot(drag_start.cross(drag_end)) > 0 else -1
                rotation = Quaternion.fromAngleAxis(direction * angle, Vector.Unit_X)
            elif self.getLockedAxis() == ToolHandle.YAxis:
                direction = 1 if Vector.Unit_Y.dot(drag_start.cross(drag_end)) > 0 else -1
                rotation = Quaternion.fromAngleAxis(direction * angle, Vector.Unit_Y)
            elif self.getLockedAxis() == ToolHandle.ZAxis:
                direction = 1 if Vector.Unit_Z.dot(drag_start.cross(drag_end)) > 0 else -1
                rotation = Quaternion.fromAngleAxis(direction * angle, Vector.Unit_Z)
            else:
                direction = -1

            # Rate-limit the angle change notification
            # This is done to prevent the UI from being flooded with property change notifications,
            # which in turn would trigger constant repaints.
            new_time = time.monotonic()
            if not self._angle_update_time or new_time - self._angle_update_time > 0.1:
                self._angle_update_time = new_time
                self._angle += direction * angle
                self.propertyChanged.emit()

                # Rotate around the saved centeres of all selected nodes
                if len(self._saved_node_positions) > 1:
                    op = GroupedOperation()
                    for node, position in self._saved_node_positions:
                        op.addOperation(RotateOperation(node, rotation, rotate_around_point = position))
                    op.push()
                else:
                    for node, position in self._saved_node_positions:
                        RotateOperation(node, rotation, rotate_around_point=position).push()

                self.setDragStart(event.x, event.y)
            return True

        if event.type == Event.MouseReleaseEvent:
            # Finish a rotate operation
            if self.getDragPlane():
                self.setDragPlane(None)
                self.setLockedAxis(ToolHandle.NoAxis)
                self._angle = None
                self.propertyChanged.emit()
                if self._rotating:
                    self.operationStopped.emit(self)
                return True

    def _onSelectedFaceChanged(self):
        if not self._select_face_mode:
            return

        self._handle.setEnabled(not Selection.getFaceSelectMode())

        selected_face = Selection.getSelectedFace()
        if not Selection.getSelectedFace() or not (Selection.hasSelection() and Selection.getFaceSelectMode()):
            return

        original_node, face_id = selected_face
        meshdata = original_node.getMeshDataTransformed()
        if not meshdata or face_id < 0:
            return

        face_mid, face_normal = meshdata.getFacePlane(face_id)
        object_mid = original_node.getBoundingBox().center
        rotation_point_vector = Vector(object_mid.x, object_mid.y, face_mid[2])
        face_normal_vector = Vector(face_normal[0], face_normal[1], face_normal[2])
        rotation_quaternion = Quaternion.rotationTo(face_normal_vector.normalized(), Vector(0.0, -1.0, 0.0))

        operation = GroupedOperation()
        current_node = None  # type: Optional[SceneNode]
        for node in Selection.getAllSelectedObjects():
            current_node = node
            parent_node = current_node.getParent()
            while parent_node and parent_node.callDecoration("isGroup"):
                current_node = parent_node
                parent_node = current_node.getParent()
        if current_node is None:
            return

        rotate_operation = RotateOperation(current_node, rotation_quaternion, rotation_point_vector)
        operation.addOperation(rotate_operation)
        operation.push()

        # NOTE: We might want to consider unchecking the select-face button afterthe operation is done.

    ##  Return a formatted angle of the current rotate operation
    #
    #   \return type(String) fully formatted string showing the angle by which the mesh(es) are rotated
    def getToolHint(self):
        return "%d°" % round(math.degrees(self._angle)) if self._angle else None

    ##  Get whether the select face feature is supported.
    #   \return True if it is supported, or False otherwise.
    def getSelectFaceSupported(self) -> bool:
        # Use a dummy postfix, since an equal version with a postfix is considered smaller normally.
        return Version(OpenGL.getInstance().getOpenGLVersion()) >= Version("4.1 dummy-postfix")

    ##  Get the state of the "snap rotation to N-degree increments" option
    #
    #   \return type(Boolean)
    def getRotationSnap(self):
        return self._snap_rotation

    ##  Set the state of the "snap rotation to N-degree increments" option
    #
    #   \param snap type(Boolean)
    def setRotationSnap(self, snap):
        if snap != self._snap_rotation:
            self._snap_rotation = snap
            self.propertyChanged.emit()

    ##  Get the number of degrees used in the "snap rotation to N-degree increments" option
    #
    #   \return type(Number)
    def getRotationSnapAngle(self):
        return self._snap_angle

    ##  Set the number of degrees used in the "snap rotation to N-degree increments" option
    #
    #   \param snap type(Number)
    def setRotationSnapAngle(self, angle):
        if angle != self._snap_angle:
            self._snap_angle = angle
            self.propertyChanged.emit()

    ##  Wether the rotate tool is in 'Lay flat by face'-Mode.
    #
    #   \return (bool)
    def getSelectFaceToLayFlatMode(self) -> bool:
        if not Selection.getFaceSelectMode():
            self._select_face_mode = False  # .. but not the other way around!
        return self._select_face_mode

    ##  Set the rotate tool to/from 'Lay flat by face'-Mode.
    #
    #   \param (bool)
    def setSelectFaceToLayFlatMode(self, select: bool) -> None:
        if select != self._select_face_mode or select != Selection.getFaceSelectMode():
            self._select_face_mode = select
            if not select:
                Selection.clearFace()
            Selection.setFaceSelectMode(self._select_face_mode)
            self.propertyChanged.emit()

    ##  Reset the orientation of the mesh(es) to their original orientation(s)
    def resetRotation(self):
        for node in self._getSelectedObjectsWithoutSelectedAncestors():
            node.setMirror(Vector(1, 1, 1))

        Selection.applyOperation(SetTransformOperation, None, Quaternion(), None)

    ##  Initialise and start a LayFlatOperation
    #
    #   Note: The LayFlat functionality is mostly used for 3d printing and should probably be moved into the Cura project
    def layFlat(self):
        self.operationStarted.emit(self)
        self._progress_message = Message(i18n_catalog.i18nc("@label", "Laying object flat on buildplate..."), lifetime = 0, dismissable = False, title = i18n_catalog.i18nc("@title", "Object Rotation"))
        self._progress_message.setProgress(0)

        self._iterations = 0
        self._total_iterations = 0
        for selected_object in self._getSelectedObjectsWithoutSelectedAncestors():
            self._layObjectFlat(selected_object)
        self._progress_message.show()

        operations = Selection.applyOperation(LayFlatOperation)
        for op in operations:
            op.progress.connect(self._layFlatProgress)

        job = LayFlatJob(operations)
        job.finished.connect(self._layFlatFinished)
        job.start()

    ##  Lays the given object flat. The given object can be a group or not.
    def _layObjectFlat(self, selected_object):
        if not selected_object.callDecoration("isGroup"):
            self._total_iterations += selected_object.getMeshData().getVertexCount() * 2
        else:
            for child in selected_object.getChildren():
                self._layObjectFlat(child)

    ##  Called while performing the LayFlatOperation so progress can be shown
    #
    #   Note that the LayFlatOperation rate-limits these callbacks to prevent the UI from being flooded with property change notifications,
    #   \param iterations type(int) number of iterations performed since the last callback
    def _layFlatProgress(self, iterations: int):
        self._iterations += iterations
        if self._progress_message:
            self._progress_message.setProgress(min(100 * (self._iterations / self._total_iterations), 100))

    ##  Called when the LayFlatJob is done running all of its LayFlatOperations
    #
    #   \param job type(LayFlatJob)
    def _layFlatFinished(self, job):
        if self._progress_message:
            self._progress_message.hide()
            self._progress_message = None

        self.operationStopped.emit(self)


##  A LayFlatJob bundles multiple LayFlatOperations for multiple selected objects
#
#   The job is executed on its own thread, processing each operation in order, so it does not lock up the GUI.
class LayFlatJob(Job):
    def __init__(self, operations):
        super().__init__()

        self._operations = operations

    def run(self):
        for op in self._operations:
            op.process()
