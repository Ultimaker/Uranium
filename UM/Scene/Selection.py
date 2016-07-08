# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal
from UM.Math.Vector import Vector
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Scene.SceneNode import SceneNode

from UM.Operations.GroupedOperation import GroupedOperation

import copy


##    This class is responsible for keeping track of what objects are selected
#     It uses signals to notify others of changes in the selection
#     It also has a convenience function that allows it to apply a single operation
#     to all selected objects.
class Selection:
    @classmethod
    def add(cls, object):
        if object not in cls.__selection:
            cls.__selection.append(object)
            object.transformationChanged.connect(cls._onTransformationChanged)
            cls._onTransformationChanged(object)
            cls.selectionChanged.emit()

    @classmethod
    def remove(cls, object):
        if object in cls.__selection:
            cls.__selection.remove(object)
            object.transformationChanged.disconnect(cls._onTransformationChanged)
            cls._onTransformationChanged(object)
            cls.selectionChanged.emit()

    @classmethod
    ##  Get number of selected objects
    def getCount(cls):
        return len(cls.__selection)

    @classmethod
    def getAllSelectedObjects(cls):
        return cls.__selection

    @classmethod
    def getBoundingBox(cls):
        bounding_box = None # don't start with an empty bounding box, because that includes (0,0,0)
        for node in cls.__selection:
            if type(node) is not SceneNode:
                continue

            if not bounding_box:
                bounding_box = node.getBoundingBox()
            else:
                bounding_box = bounding_box + node.getBoundingBox()

        if not bounding_box:
            bounding_box = AxisAlignedBox.Null

        return bounding_box

    @classmethod
    ##  Get selected object by index
    #   \param index index of the objectto return
    #   \returns selected object or None if index was incorrect / not found
    def getSelectedObject(cls, index):
        try:
            return cls.__selection[index]
        except:
            return None

    @classmethod
    def isSelected(cls, object):
        return object in cls.__selection

    @classmethod
    def clear(cls):
        cls.__selection.clear()
        cls.selectionChanged.emit()

    @classmethod
    ##  Check if anything is selected at all.
    def hasSelection(cls):
        return bool(cls.__selection)

    selectionChanged = Signal()

    selectionCenterChanged = Signal()

    @classmethod
    def getSelectionCenter(cls):
        if not cls.__selection:
            cls.__selection_center = Vector.Null

        return cls.__selection_center

    ##  Apply an operation to the entire selection
    #
    #   This will create and push an operation onto the operation stack. Dependent
    #   on whether there is one item selected or multiple it will be just the
    #   operation or a grouped operation containing the operation for each selected
    #   node.
    #
    #   \param operation \type{Class} The operation to create and push. It should take a SceneNode as first positional parameter.
    #   \param args The additional positional arguments passed along to the operation constructor.
    #   \param kwargs The additional keyword arguements that will be passed along to the operation constructor.
    #
    #   \return list of instantiated operations
    @classmethod
    def applyOperation(cls, operation, *args, **kwargs):
        if not cls.__selection:
            return

        operations = []

        if len(cls.__selection) == 1:
            node = cls.__selection[0]
            op = operation(node, *args, **kwargs)
            operations.append(op)
        else:
            op = GroupedOperation()

            for node in Selection.getAllSelectedObjects():
                sub_op = operation(node, *args, **kwargs)
                op.addOperation(sub_op)
                operations.append(sub_op)

        op.push()
        return operations

    @classmethod
    def _onTransformationChanged(cls, node):
        cls.__selection_center = Vector.Null

        for object in cls.__selection:
            cls.__selection_center = cls.__selection_center + object.getWorldPosition()

        cls.__selection_center = cls.__selection_center / len(cls.__selection)

        cls.selectionCenterChanged.emit()

    __selection = []
    __selection_center = Vector(0, 0, 0)
