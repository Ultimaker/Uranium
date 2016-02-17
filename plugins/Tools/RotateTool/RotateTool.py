# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Job import Job
from UM.Event import Event, MouseEvent, KeyEvent
from UM.Application import Application
from UM.Message import Message
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion
from UM.Math.Float import Float

from UM.Operations.RotateOperation import RotateOperation
from UM.Operations.TranslateOperation import TranslateOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.SetTransformOperation import SetTransformOperation
from UM.Operations.LayFlatOperation import LayFlatOperation

from . import RotateToolHandle

import math
import time

class RotateTool(Tool):
    def __init__(self):
        super().__init__()
        self._handle = RotateToolHandle.RotateToolHandle()

        self._snap_rotation = True
        self._snap_angle = math.radians(15)

        self._angle = None
        self._angle_update_time = None

        self._progress_message = None
        self._iterations = 0
        self._total_iterations = 0

        self.setExposedProperties("Rotation", "RotationSnap", "RotationSnapAngle")

    def event(self, event):
        super().event(event)

        if event.type == Event.KeyPressEvent and event.key == KeyEvent.ShiftKey:
            self._snap_rotation = (not self._snap_rotation)
            self.propertyChanged.emit()

        if event.type == Event.KeyReleaseEvent and event.key == KeyEvent.ShiftKey:
            self._snap_rotation = (not self._snap_rotation)
            self.propertyChanged.emit()

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._selection_pass.getIdAtPosition(event.x, event.y)
            if not id:
                return

            if ToolHandle.isAxis(id):
                self.setLockedAxis(id)
                handle_position = self._handle.getWorldPosition()

                if id == ToolHandle.XAxis:
                    self.setDragPlane(Plane(Vector(1, 0, 0), handle_position.x))
                elif id == ToolHandle.YAxis:
                    self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))
                elif self._locked_axis == ToolHandle.ZAxis:
                    self.setDragPlane(Plane(Vector(0, 0, 1), handle_position.z))

                self.setDragStart(event.x, event.y)
                self._angle = 0
                self.operationStarted.emit(self)

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            if not self.getDragStart():
                self.setDragStart(event.x, event.y)

            handle_position = self._handle.getWorldPosition()

            drag_start = (self.getDragStart() - handle_position).normalize()
            drag_position = self.getDragPosition(event.x, event.y)
            if not drag_position:
                return
            drag_end = (drag_position - handle_position).normalize()

            try:
                angle = math.acos(drag_start.dot(drag_end))
            except ValueError:
                angle = 0

            if self._snap_rotation:
                angle = int(angle / self._snap_angle) * self._snap_angle
                if angle == 0:
                    return

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

            self._angle += direction * angle

            # Rate-limit the angle change notification
            # This is done to prevent the UI from being flooded with property change notifications,
            # which in turn would trigger constant repaints.
            new_time = time.monotonic()
            if not self._angle_update_time or new_time - self._angle_update_time > 0.01:
                self.propertyChanged.emit()
                self._angle_update_time = new_time

            Selection.applyOperation(RotateOperation, rotation, rotate_around_point = handle_position)

            self.setDragStart(event.x, event.y)

        if event.type == Event.MouseReleaseEvent:
            if self.getDragPlane():
                self.setDragPlane(None)
                self.setLockedAxis(None)
                self._angle = None
                self.propertyChanged.emit()
                self.operationStopped.emit(self)
                return True

    def getRotation(self):
        return round(math.degrees(self._angle)) if self._angle else None

    def getRotationSnap(self):
        return self._snap_rotation

    def setRotationSnap(self, snap):
        if snap != self._snap_rotation:
            self._snap_rotation = snap
            self.propertyChanged.emit()

    def getRotationSnapAngle(self):
        return self._snap_angle

    def setRotationSnapAngle(self, angle):
        if angle != self._snap_angle:
            self._snap_angle = angle
            self.propertyChanged.emit()

    def resetRotation(self):
        Selection.applyOperation(SetTransformOperation, None, Quaternion(), None)

    def layFlat(self):
        self.operationStarted.emit(self)
        self._progress_message = Message("Laying object flat on buildplate...", lifetime = 0, dismissable = False)
        self._progress_message.setProgress(0)

        self._iterations = 0
        self._total_iterations = 0
        for selected_object in Selection.getAllSelectedObjects():
            self._total_iterations += len(selected_object.getMeshDataTransformed().getVertices()) * 2

        self._progress_message.show()

        operations = Selection.applyOperation(LayFlatOperation)
        for op in operations:
            op.progress.connect(self._layFlatProgress)

        job = LayFlatJob(operations)
        job.finished.connect(self._layFlatFinished)
        job.start()

    def _layFlatProgress(self, iterations):
        self._iterations += iterations
        self._progress_message.setProgress(100 * self._iterations / self._total_iterations)

    def _layFlatFinished(self, job):
        if self._progress_message:
            self._progress_message.hide()
            self._progress_message = None

        self.operationStopped.emit(self)

class LayFlatJob(Job):
    def __init__(self, operations):
        super().__init__()

        self._operations = operations

    def run(self):
        for op in self._operations:
            op.process()
