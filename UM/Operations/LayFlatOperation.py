# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import Operation

from UM.Scene.SceneNode import SceneNode
from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion

from UM.Signal import Signal

import math
import time
import numpy


class LayFlatOperation(Operation.Operation):
    """Operation that lays a mesh flat on the scene."""

    progress = Signal()
    """Signal that indicates that the progress meter has changed."""

    def __init__(self, node, orientation = None):
        """Creates the operation.

        An optional orientation may be added if the answer of this lay flat
        operation is already known. This may occur if two lay flat operations
        are combined.

        :param node: The scene node to apply the operation on.
        :param orientation: A pre-calculated result orientation.
        """

        super().__init__()
        self._node = node #Node the operation is applied on.

        self._progress_emit_time = None #Time when the progress signal was most recently emitted.
        self._progress = 0 #Current progress. Expressed in number of vertices it has processed (ranging from 0 to n).

        self._old_orientation = node.getOrientation() #Orientation before laying it flat.
        if orientation:
            self._new_orientation = orientation #Orientation after laying it flat.
        else:
            self._new_orientation = self._old_orientation

    def process(self):
        """Computes some orientation to hopefully lay the object flat.

        No promises! This algorithm finds the lowest three vertices and lays
        them flat. This is a rather naive heuristic, but fast and practical.
        """

        # Based on https://github.com/daid/Cura/blob/SteamEngine/Cura/util/printableObject.py#L207
        # Note: Y & Z axis are swapped

        #Transform mesh first to get the current positions of the vertices.
        transformed_vertices = self._node.getMeshDataTransformedVertices()

        min_y_vertex = transformed_vertices[transformed_vertices.argmin(0)[1]]
        dot_min = 1.0 #Minimum y-component of direction vector.
        dot_v = None

        #Find the second-lowest vertex.
        for v in transformed_vertices:
            diff = v - min_y_vertex #From this vertex to the lowest vertex.
            length = math.sqrt(diff[0] * diff[0] + diff[1] * diff[1] + diff[2] * diff[2])
            if length < 5: #Ignore lines smaller than half a centimetre. It's unreliable at such small distances.
                continue
            dot = (diff[1] / length) #Y-component of direction vector.
            if dot_min > dot:
                dot_min = dot
                dot_v = diff
            self._emitProgress(1)

        if dot_v is None: #Couldn't find any vertex further than 5mm from the lowest vertex.
            self._emitProgress(len(transformed_vertices))
            return

        #Rotate the mesh such that the second-lowest vertex is just as low as the lowest vertex.
        rad = math.atan2(dot_v[2], dot_v[0])
        self._node.rotate(Quaternion.fromAngleAxis(rad, Vector.Unit_Y), SceneNode.TransformSpace.Parent)
        rad = -math.asin(dot_min)
        self._node.rotate(Quaternion.fromAngleAxis(rad, Vector.Unit_Z), SceneNode.TransformSpace.Parent)

        #Apply the transformation so we get new vertex coordinates.
        transformed_vertices = self._node.getMeshDataTransformedVertices()

        min_y_vertex = transformed_vertices[transformed_vertices.argmin(0)[1]]
        dot_min = 1.0
        dot_v = None

        #Find the second-lowest vertex again.
        for v in transformed_vertices:
            diff = v - min_y_vertex #From this vertex to the lowest vertex.
            length = math.sqrt(diff[2] * diff[2] + diff[1] * diff[1])
            if length < 5: #Ignore lines smaller than half a centimetre. It's unreliable at such small distances.
                continue
            dot = (diff[1] / length) #Y-component of direction vector.
            if dot_min > dot:
                dot_min = dot
                dot_v = diff
            self._emitProgress(1)

        if dot_v is None: #Couldn't find any vertex further than 5mm from the lowest vertex.
            self._node.setOrientation(self._old_orientation)
            return

        #Rotate the mesh such that the second-lowest vertex gets the same height as the lowest vertex.
        if dot_v[2] < 0:
            rad = -math.asin(dot_min)
        else:
            rad = math.asin(dot_min)
        self._node.rotate(Quaternion.fromAngleAxis(rad, Vector.Unit_X), SceneNode.TransformSpace.Parent)

        self._new_orientation = self._node.getOrientation() #Save the resulting orientation.

    def _emitProgress(self, progress):
        """Increments the progress.

        This lets the progress bar update to give the user an impression of how
        long he still has to wait.

        :param progress: The amount of progress made since the last emission.
        """

        # Rate-limited progress notification
        # This is done to prevent the UI from being flooded with progress signals.
        self._progress += progress
        new_time = time.monotonic()
        if not self._progress_emit_time or new_time - self._progress_emit_time > 0.5: #Must be longer than half a second ago.
            self._progress_emit_time = new_time
            self.progress.emit(self._progress)
            self._progress = 0

    def undo(self):
        """Undoes this lay flat operation."""

        self._node.setOrientation(self._old_orientation) #Restore saved orientation.

    def redo(self):
        """Re-does this lay flat operation."""

        if self._new_orientation: #Only if the orientation was finished calculating.
            self._node.setOrientation(self._new_orientation)
            pass

    def mergeWith(self, other):
        """Merge this lay flat operation with another lay flat operation.

        If multiple lay flat operations are executed in sequence, the user needs
        to press undo only once to undo them all.

        You should ONLY merge a lay flat operation with an older operation. It
        is NOT symmetric.

        :param other: The lay flat operation to merge this operation with. The
        specified operation must be an older operation than this operation.
        :return: True if the merge was successful, or False otherwise.
        """

        if type(other) is not LayFlatOperation: #Must be a LayFlatOperation.
            return False

        if other._node != self._node: #Must be on the same node.
            return False

        if other._new_orientation is None or self._new_orientation is None: #Both must have been valid operations (completed computation).
            return False

        op = LayFlatOperation(self._node, self._new_orientation) #Use the same new orientation as this one.
        op._old_orientation = other._old_orientation #But use the old orientation of the other one.
        return op

    def __repr__(self):
        """Makes a programmer-readable representation of this operation."""

        return "LayFlatOp.(node={0})".format(self._node)
