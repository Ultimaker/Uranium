# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation
from UM.Scene.SceneNode import SceneNode
from UM.Math.Vector import Vector
import copy


class ScaleOperation(Operation.Operation):
    def __init__(self, node, scale, **kwargs):
        super().__init__()
        self._node = node
        self._old_transformation = node.getLocalTransformation()
        self._set_scale = kwargs.get("set_scale", False)
        self._add_scale = kwargs.get("add_scale", False)
        self._relative_scale = kwargs.get("relative_scale", False)
        self._scale_around_point = kwargs.get("scale_around_point" , Vector(0,0,0))
        self._snap = kwargs.get("snap", False)
        self._scale = scale
        self._min_scale = 0.01

    def undo(self):
        self._node.setTransformation(self._old_transformation)

    def redo(self):
        if self._set_scale:
            self._node.setScale(self._scale, SceneNode.TransformSpace.World)
        elif self._add_scale:
            self._node.setScale(self._node.getScale() + self._scale)
        elif self._relative_scale:
            scale_factor = Vector()
            ## Ensure that the direction is correctly applied (it can be flipped due to mirror)
            if self._scale.z == self._scale.y and self._scale.y == self._scale.x:
                ratio = (1 / (self._node.getScale().x + self._node.getScale().y + self._node.getScale().z)) * 3
                ratio_vector = ratio * copy.deepcopy(self._node.getScale())
                self._scale = ratio_vector * self._scale
            if self._node.getScale().x > 0:
                scale_factor.setX(abs(self._node.getScale().x + self._scale.x))
            else:
                scale_factor.setX(-abs(self._node.getScale().x - self._scale.x))
            if self._node.getScale().y > 0:
                scale_factor.setY(abs(self._node.getScale().y + self._scale.y))
            else:
                scale_factor.setY(-abs(self._node.getScale().y - self._scale.y))
            if self._node.getScale().z > 0:
                scale_factor.setZ(abs(self._node.getScale().z + self._scale.z))
            else:
                scale_factor.setZ(-abs(self._node.getScale().z - self._scale.z))

            current_scale = copy.deepcopy(self._node.getScale())

            if scale_factor.x != 0:
                scale_factor.setX(scale_factor.x / current_scale.x)
            if scale_factor.y != 0:
                scale_factor.setY(scale_factor.y / current_scale.y)
            if scale_factor.z != 0:
                scale_factor.setZ(scale_factor.z / current_scale.z)

            self._node.setPosition(-self._scale_around_point)
            self._node.scale(scale_factor, SceneNode.TransformSpace.Parent)
            self._node.setPosition(self._scale_around_point)
            new_scale = copy.deepcopy(self._node.getScale())
            if self._snap:
                if(scale_factor.x != 1.0):
                    new_scale.setX(round(new_scale.x, 2))
                if(scale_factor.y != 1.0):
                    new_scale.setY(round(new_scale.y, 2))
                if(scale_factor.z != 1.0):
                    new_scale.setZ(round(new_scale.z, 2))

            # Enforce min size.
            if new_scale.x < self._min_scale and new_scale.x >=0:
                new_scale.setX(self._min_scale)
            if new_scale.y < self._min_scale and new_scale.y >=0:
                new_scale.setY(self._min_scale)
            if new_scale.z < self._min_scale and new_scale.z >=0:
                new_scale.setZ(self._min_scale)

            # Enforce min size (when mirrored)
            if new_scale.x > -self._min_scale and new_scale.x <=0:
                new_scale.setX(-self._min_scale)
            if new_scale.y > -self._min_scale and new_scale.y <=0:
                new_scale.setY(-self._min_scale)
            if new_scale.z > -self._min_scale and new_scale.z <=0:
                new_scale.setZ(-self._min_scale)
            self._node.setScale(new_scale, SceneNode.TransformSpace.World)
        else:
            self._node.scale(self._scale, SceneNode.TransformSpace.World)

    def mergeWith(self, other):
        if type(other) is not ScaleOperation:
            return False

        if other._node != self._node:
            return False

        if other._set_scale and not self._set_scale:
            return False

        if other._add_scale and not self._add_scale:
            return False

        op = ScaleOperation(self._node, self._scale)
        op._old_transformation = other._old_transformation
        return op

    def __repr__(self):
        return "ScaleOperation(node = {0}, scale={1})".format(self._node, self._scale)

