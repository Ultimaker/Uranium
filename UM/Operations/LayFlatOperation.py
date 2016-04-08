# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

from UM.Scene.SceneNode import SceneNode
from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion

from UM.Signal import Signal

import math
import time


class LayFlatOperation(Operation.Operation):
    progress = Signal()

    def __init__(self, node, orientation = None):
        super().__init__()
        self._node = node

        self._progress_emit_time = None
        self._progress = 0

        self._old_orientation = node.getOrientation()
        if orientation:
            self._new_orientation = orientation
        else:
            self._new_orientation = self._old_orientation

    def process(self):
        # Based on https://github.com/daid/Cura/blob/SteamEngine/Cura/util/printableObject.py#L207
        # Note: Y & Z axis are swapped

        transformed_vertices = self._node.getMeshDataTransformed().getVertices()
        min_y_vertex = transformed_vertices[transformed_vertices.argmin(0)[1]]
        dot_min = 1.0
        dot_v = None

        for v in transformed_vertices:
            diff = v - min_y_vertex
            length = math.sqrt(diff[0] * diff[0] + diff[2] * diff[2] + diff[1] * diff[1])
            if length < 5:
                continue
            dot = (diff[1] / length)
            if dot_min > dot:
                dot_min = dot
                dot_v = diff
            self._emitProgress(1)

        if dot_v is None:
            self._emitProgress(len(transformed_vertices))
            return

        rad = math.atan2(dot_v[2], dot_v[0])
        self._node.rotate(Quaternion.fromAngleAxis(rad, Vector.Unit_Y), SceneNode.TransformSpace.Parent)


        rad = -math.asin(dot_min)
        self._node.rotate(Quaternion.fromAngleAxis(rad, Vector.Unit_Z), SceneNode.TransformSpace.Parent)

        transformed_vertices = self._node.getMeshDataTransformed().getVertices()
        min_y_vertex = transformed_vertices[transformed_vertices.argmin(0)[1]]
        dot_min = 1.0
        dot_v = None

        for v in transformed_vertices:
            diff = v - min_y_vertex
            length = math.sqrt(diff[2] * diff[2] + diff[1] * diff[1])
            if length < 5:
                continue
            dot = (diff[1] / length)
            if dot_min > dot:
                dot_min = dot
                dot_v = diff
            self._emitProgress(1)

        if dot_v is None:
            self._node.setOrientation(self._old_orientation)
            return

        if dot_v[2] < 0:
            rad = -math.asin(dot_min)
        else:
            rad = math.asin(dot_min)
        self._node.rotate(Quaternion.fromAngleAxis(rad, Vector.Unit_X), SceneNode.TransformSpace.Parent)

        self._new_orientation = self._node.getOrientation()

    def _emitProgress(self, progress):
        # Rate-limited progress notification
        # This is done to prevent the UI from being flooded with progress signals.
        self._progress += progress

        new_time = time.monotonic()
        if not self._progress_emit_time or new_time - self._progress_emit_time > 0.5:
            self.progress.emit(self._progress)
            self._progress_emit_time = new_time
            self._progress = 0

    def undo(self):
        self._node.setOrientation(self._old_orientation)

    def redo(self):
        if self._new_orientation:
            self._node.setOrientation(self._new_orientation)
            pass

    def mergeWith(self, other):
        if type(other) is not LayFlatOperation:
            return False

        if other._node != self._node:
            return False

        if other._new_orientation is None or self._new_orientation is None:
            return False

        op = LayFlatOperation(self._node, self._new_orientation)
        op._old_orientation = other._old_orientation
        return op

    def __repr__(self):
        return "LayFlatOperation(node = {0})".format(self._node)
