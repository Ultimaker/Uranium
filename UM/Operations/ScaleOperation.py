# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import copy

from . import Operation
from UM.Scene.SceneNode import SceneNode #To get the world transformation.
from UM.Math.Vector import Vector

class ScaleOperation(Operation.Operation):
    """Operation that scales a scene node, uniformly or non-uniformly."""

    def __init__(self, node, scale, set_scale = False, add_scale = False, relative_scale = False, scale_around_point = Vector(0, 0, 0), snap = False):
        """Initialises the scale operation.

        :param node: The scene node to scale.
        :param scale: A matrix to scale the node with. This matrix should only be
        non-zero on the diagonal.
        :param set_scale: Whether to simply replace the old scale with the new
        one (True) or modify the old scale (False).
        :param add_scale: Whether to add to the old scale (True) or multiply with
        it (False).
        :param relative_scale: Whether to multiply the scale relative to the
        current scale (True) or simply multiply it with a constant (False).
        :param scale_around_point: All coordinates are moved away from or towards
        this point.
        :param snap: Whether to use snap scaling (True) or not (False).
        """

        super().__init__()
        self._node = node #The scene node to scale.
        self._old_transformation = node.getLocalTransformation() #The transformation of the node before scaling.
        self._set_scale = set_scale #Whether to simply change the scale.
        self._add_scale = add_scale #Whether to add to the old scale.
        self._relative_scale = relative_scale #Whether to multiply relatively.
        self._scale_around_point = scale_around_point #The origin of the scale operation.
        self._snap = snap #Use snap scaling?
        self._scale = scale #The transformation matrix that scales space correctly.
        self._min_scale = 0.01 #A minimum scale factor. Much lower would introduce rounding errors.

    def undo(self):
        """Undo the scale operation."""

        self._node.setTransformation(self._old_transformation)

    def redo(self):
        """Redo the scale operation."""

        if self._set_scale: #Simply change the scale.
            self._node.setScale(self._scale, SceneNode.TransformSpace.World)
        elif self._add_scale: #Add to the current scale.
            self._node.setScale(self._node.getScale() + self._scale)
        elif self._relative_scale: #Scale relatively to the current scale.
            scale_factor = Vector()
            ## Ensure that the direction is correctly applied (it can be flipped due to mirror)
            if self._scale.z == self._scale.y and self._scale.y == self._scale.x:
                ratio = (1 / (self._node.getScale().x + self._node.getScale().y + self._node.getScale().z)) * 3
                ratio_vector = ratio * self._node.getScale()
                self._scale *= ratio_vector
            if self._node.getScale().x > 0:
                scale_factor = scale_factor.set(x=abs(self._node.getScale().x + self._scale.x))
            else:
                scale_factor = scale_factor.set(x=-abs(self._node.getScale().x - self._scale.x))
            if self._node.getScale().y > 0:
                scale_factor = scale_factor.set(y=abs(self._node.getScale().y + self._scale.y))
            else:
                scale_factor = scale_factor.set(y=-abs(self._node.getScale().y - self._scale.y))
            if self._node.getScale().z > 0:
                scale_factor = scale_factor.set(z=abs(self._node.getScale().z + self._scale.z))
            else:
                scale_factor = scale_factor.set(z=-abs(self._node.getScale().z - self._scale.z))

            current_scale = self._node.getScale()

            if scale_factor.x != 0:
                scale_factor = scale_factor.set(x=scale_factor.x / current_scale.x)
            if scale_factor.y != 0:
                scale_factor = scale_factor.set(y=scale_factor.y / current_scale.y)
            if scale_factor.z != 0:
                scale_factor = scale_factor.set(z=scale_factor.z / current_scale.z)

            self._node.setPosition(-self._scale_around_point) #If scaling around a point, shift that point to the axis origin first and shift it back after performing the transformation.
            self._node.scale(scale_factor, SceneNode.TransformSpace.Parent)
            self._node.setPosition(self._scale_around_point)
            new_scale = self._node.getScale()
            if self._snap:
                if scale_factor.x != 1.0:
                    new_scale = new_scale.set(x=round(new_scale.x, 2))
                if scale_factor.y != 1.0:
                    new_scale = new_scale.set(y=round(new_scale.y, 2))
                if scale_factor.z != 1.0 :
                    new_scale = new_scale.set(z=round(new_scale.z, 2))

            # Enforce min size.
            if new_scale.x < self._min_scale and new_scale.x >= 0:
                new_scale = new_scale.set(x=self._min_scale)
            if new_scale.y < self._min_scale and new_scale.y >= 0:
                new_scale = new_scale.set(y=self._min_scale)
            if new_scale.z < self._min_scale and new_scale.z >= 0:
                new_scale = new_scale.set(z=self._min_scale)

            # Enforce min size (when mirrored)
            if new_scale.x > -self._min_scale and new_scale.x <= 0:
                new_scale = new_scale.set(x=-self._min_scale)
            if new_scale.y > -self._min_scale and new_scale.y <= 0:
                new_scale = new_scale.set(y=-self._min_scale)
            if new_scale.z > -self._min_scale and new_scale.z <=0:
                new_scale = new_scale.set(z=-self._min_scale)
            self._node.setScale(new_scale, SceneNode.TransformSpace.World)
        else:
            self._node.setPosition(-self._scale_around_point, SceneNode.TransformSpace.World)  # If scaling around a point, shift that point to the axis origin first and shift it back after performing the transformation.
            self._node.scale(self._scale, SceneNode.TransformSpace.World) #Default to _set_scale
            self._node.setPosition(self._scale_around_point, SceneNode.TransformSpace.World)  # If scaling around a point, shift that point to the axis origin first and shift it back after performing the transformation.

    def mergeWith(self, other):
        """Merge this operation with another scale operation.

        This prevents the user from having to undo multiple operations if they
        were not his operations.

        You should ONLY merge this operation with an older operation. It is NOT
        symmetric.

        :param other: The older scale operation to merge this operation with.
        :return: A new operation that performs both scale operations.
        """

        if type(other) is not ScaleOperation:
            return False
        if other._node != self._node: #Must be scaling the same node.
            return False
        if other._set_scale and not self._set_scale: #Must be the same type of scaling.
            return False
        if other._add_scale and not self._add_scale:
            return False
        if other._relative_scale and not self._relative_scale:
            return False
        if other._scale_around_point != self._scale_around_point:
            return False
        if other._snap != self._snap:
            return False

        op = ScaleOperation(self._node, self._scale + other._scale, set_scale = self._set_scale, add_scale = self._add_scale, relative_scale = self._relative_scale, scale_around_point = self._scale_around_point, snap = self._snap)
        op._old_transformation = copy.deepcopy(other._old_transformation) #Use the oldest transformation of the two.
        return op

    def __repr__(self):
        """Returns a programmer-readable representation of this operation.

        :return: A programmer-readable representation of this operation.
        """

        mode = "set" if self._set_scale else "add" if self._add_scale else "relative"
        return "ScaleOp.(node={0},scale={1},mode={2})".format(self._node, self._scale, mode)

