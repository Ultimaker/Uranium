# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

from UM.Scene.SceneNode import SceneNode
from UM.Math.Matrix import Matrix
from UM.Math.Quaternion import Quaternion

import math


class LayFlatOperation(Operation.Operation):

    def __init__(self, node, orientation = None):
        super().__init__()
        self._node = node

        self._old_orientation = node.getOrientation()
        self._new_orientation = orientation

        if orientation:
            return
        
        # Based on https://github.com/daid/Cura/blob/SteamEngine/Cura/util/printableObject.py#L207
        # Note: Y & Z axis are swapped

        transformed_vertices = node.getMeshDataTransformed().getVertices()
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

        if dot_v is None:
            return

        rad = -math.asin(dot_min)

        m = Matrix([
            [ math.cos(rad), math.sin(rad), 0 ],
            [-math.sin(rad), math.cos(rad), 0 ],
            [ 0,             0,             1 ]
        ])
        node.rotate(Quaternion.fromMatrix(m), SceneNode.TransformSpace.Parent)

        rad = math.atan2(dot_v[2], dot_v[0])
        m = Matrix([
            [ math.cos(rad), 0, math.sin(rad)],
            [ 0,             1, 0 ],
            [-math.sin(rad), 0, math.cos(rad)]
        ])
        node.rotate(Quaternion.fromMatrix(m), SceneNode.TransformSpace.Parent)

        transformed_vertices = node.getMeshDataTransformed().getVertices()
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

        if dot_v is None:
            node.setOrientation(self._old_orientation)
            return

        if dot_v[2] < 0:
            rad = -math.asin(dot_min)
        else:
            rad = math.asin(dot_min)
        m = Matrix([
            [ 1, 0,             0 ],
            [ 0, math.cos(rad),-math.sin(rad) ],
            [ 0, math.sin(rad), math.cos(rad) ]
        ])
        node.rotate(Quaternion.fromMatrix(m), SceneNode.TransformSpace.Parent)

        self._new_orientation = node.getOrientation()
        node.setOrientation(self._old_orientation)

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
