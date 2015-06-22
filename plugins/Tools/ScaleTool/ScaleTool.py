# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent, KeyEvent
from UM.Application import Application
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection
from UM.Math.Plane import Plane
from UM.Math.Vector import Vector

from UM.Operations.ScaleOperation import ScaleOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.SetTransformOperation import SetTransformOperation
from UM.Operations.ScaleToBoundsOperation import ScaleToBoundsOperation

from . import ScaleToolHandle

class ScaleTool(Tool):
    def __init__(self):
        super().__init__()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = ScaleToolHandle.ScaleToolHandle()

        self._snap_scale = True
        self._snap_amount = 0.05
        self._non_uniform_scale = False

        self._drag_length = 0

        self._maximum_bounds = None

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
        super().event(event)

        if event.type == Event.ToolActivateEvent:
            for node in Selection.getAllSelectedObjects():
                node.boundingBoxChanged.connect(self.propertyChanged)

        if event.type == Event.ToolDeactivateEvent:
            for node in Selection.getAllSelectedObjects():
                node.boundingBoxChanged.disconnect(self.propertyChanged)

        if event.type == Event.KeyPressEvent:
            if event.key == KeyEvent.ShiftKey:
                self._lock_steps = False
                self.propertyChanged.emit()
            elif event.key == KeyEvent.ControlKey:
                self._non_uniform_scale = True
                self.propertyChanged.emit()

        if event.type == Event.KeyReleaseEvent:
            if event.key == KeyEvent.ShiftKey:
                self._lock_steps = True
                self.propertyChanged.emit()
            elif event.key == KeyEvent.ControlKey:
                self._non_uniform_scale = False
                self.propertyChanged.emit()

        if event.type == Event.MousePressEvent:
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return False

            if ToolHandle.isAxis(id):
                self.setLockedAxis(id)

            handle_position = self._handle.getWorldPosition()

            if id == ToolHandle.XAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), handle_position.z))
            elif id == ToolHandle.YAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), handle_position.z))
            elif id == ToolHandle.ZAxis:
                self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))
            else:
                self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))

            self.setDragStart(event.x, event.y)
            self.operationStarted.emit(self)

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            handle_position = self._handle.getWorldPosition()
            drag_position = self.getDragPosition(event.x, event.y)
            if drag_position:
                drag_length = (drag_position - handle_position).length()
                if self._drag_length > 0:
                    drag_change = (drag_length - self._drag_length) / 100

                    if self._snap_scale and abs(drag_change) < self._snap_amount:
                        return False

                    scale = Vector(1.0, 1.0, 1.0)
                    if self._non_uniform_scale:
                        if self.getLockedAxis() == ToolHandle.XAxis:
                            scale.setX(1.0 + drag_change)
                        elif self.getLockedAxis() == ToolHandle.YAxis:
                            scale.setY(1.0 + drag_change)
                        elif self.getLockedAxis() == ToolHandle.ZAxis:
                            scale.setZ(1.0 + drag_change)

                    if scale == Vector(1.0, 1.0, 1.0):
                        scale.setX(1.0 + drag_change)
                        scale.setY(1.0 + drag_change)
                        scale.setZ(1.0 + drag_change)

                    Selection.applyOperation(ScaleOperation, scale)

                self._drag_length = (handle_position - drag_position).length()
                self.updateHandlePosition()
                return True

        if event.type == Event.MouseReleaseEvent:
            if self.getDragPlane():
                self.setDragPlane(None)
                self.setLockedAxis(None)
                self._drag_length = 0
                self.operationStopped.emit(self)
                return True

    def resetScale(self):
        Selection.applyOperation(SetTransformOperation, None, None, Vector(1.0, 1.0, 1.0))

    def scaleToMax(self):
        if self._maximum_bounds:
            Selection.applyOperation(ScaleToBoundsOperation, self._maximum_bounds)

    def getNonUniformScale(self):
        return self._non_uniform_scale

    def setNonUniformScale(self, scale):
        if scale != self._non_uniform_scale:
            self._non_uniform_scale = scale
            self.propertyChanged.emit()

    def getScaleSnap(self):
        return self._snap_scale

    def setScaleSnap(self, snap):
        if self._snap_scale != snap:
            self._snap_scale = snap
            self.propertyChanged.emit()

    def setMaximumBounds(self, bounds):
        self._maximum_bounds = bounds

    def getObjectWidth(self):
        if Selection.hasSelection():
            return round(float(Selection.getSelectedObject(0).getBoundingBox().width), 1)

        return 0.0

    def getObjectHeight(self):
        if Selection.hasSelection():
            return round(float(Selection.getSelectedObject(0).getBoundingBox().height), 1)

        return 0.0

    def getObjectDepth(self):
        if Selection.hasSelection():
            return round(float(Selection.getSelectedObject(0).getBoundingBox().depth), 1)

        return 0.0

    def getScaleX(self):
        if Selection.hasSelection():
            return round(float(Selection.getSelectedObject(0).getScale().x), 3)

        return 1.0

    def getScaleY(self):
        if Selection.hasSelection():
            return round(float(Selection.getSelectedObject(0).getScale().y), 3)

        return 1.0

    def getScaleZ(self):
        if Selection.hasSelection():
            return round(float(Selection.getSelectedObject(0).getScale().z), 3)

        return 1.0

    def setObjectWidth(self, width):
        obj = Selection.getSelectedObject(0)
        obj_scale = obj.getScale()
        obj_width = obj.getBoundingBox().width / obj_scale.x
        target_scale = float(width) / obj_width
        if obj_scale.x != target_scale:
            obj_scale.setX(target_scale)
            if not self._non_uniform_scale:
                obj_scale.setY(target_scale)
                obj_scale.setZ(target_scale)
            operation = SetTransformOperation(obj, None, None, obj_scale)
            operation.push()

    def setObjectHeight(self, height):
        obj = Selection.getSelectedObject(0)
        obj_scale = obj.getScale()
        obj_height = obj.getBoundingBox().height / obj_scale.y
        target_scale = float(height) / obj_height
        if obj_scale.y != target_scale:
            obj_scale.setY(target_scale)
            if not self._non_uniform_scale:
                obj_scale.setX(target_scale)
                obj_scale.setZ(target_scale)
            operation = SetTransformOperation(obj, None, None, obj_scale)
            operation.push()

    def setObjectDepth(self, depth):
        obj = Selection.getSelectedObject(0)
        obj_scale = obj.getScale()
        obj_depth = obj.getBoundingBox().depth / obj_scale.z
        target_scale = float(depth) / obj_depth
        if obj_scale.z != target_scale:
            obj_scale.setZ(target_scale)
            if not self._non_uniform_scale:
                obj_scale.setY(target_scale)
                obj_scale.setX(target_scale)
            operation = SetTransformOperation(obj, None, None, obj_scale)
            operation.push()

    def setScaleX(self, scale):
        obj = Selection.getSelectedObject(0)
        obj_scale = obj.getScale()
        if obj_scale.x != scale:
            obj_scale.setX(scale)
            if not self._non_uniform_scale:
                obj_scale.setY(scale)
                obj_scale.setZ(scale)
            operation = SetTransformOperation(obj, None, None, obj_scale)
            operation.push()

    def setScaleY(self, scale):
        obj = Selection.getSelectedObject(0)
        obj_scale = obj.getScale()
        if obj_scale.y != scale:
            obj_scale.setY(scale)
            if not self._non_uniform_scale:
                obj_scale.setX(scale)
                obj_scale.setZ(scale)
            operation = SetTransformOperation(obj, None, None, obj_scale)
            operation.push()

    def setScaleZ(self, scale):
        obj = Selection.getSelectedObject(0)
        obj_scale = obj.getScale()
        if obj_scale.z != scale:
            obj_scale.setZ(scale)
            if not self._non_uniform_scale:
                obj_scale.setY(scale)
                obj_scale.setX(scale)
            operation = SetTransformOperation(obj, None, None, obj_scale)
            operation.push()
