# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal
from UM.Math.Vector import Vector

class Selection:
    @classmethod
    def add(cls, object):
        if object not in cls.__selection:
            cls.__selection.append(object)
            cls.selectionChanged.emit()

    @classmethod
    def remove(cls, object):
        if object in cls.__selection:
            cls.__selection.remove(object)
            cls.selectionChanged.emit()

    @classmethod
    def getCount(cls):
        return len(cls.__selection)

    @classmethod
    def getAllSelectedObjects(cls):
        return cls.__selection

    @classmethod
    def getSelectedObject(cls, index):
        return cls.__selection[index]

    @classmethod
    def isSelected(cls, object):
        return object in cls.__selection

    @classmethod
    def clear(cls):
        cls.__selection.clear()
        cls.selectionChanged.emit()

    @classmethod
    def hasSelection(cls):
        return bool(cls.__selection)

    selectionChanged = Signal()

    ##  Calculate the average position of the selection.
    @classmethod
    def getAveragePosition(cls):
        if not cls.__selection:
            return Vector(0, 0, 0)

        if len(cls.__selection) == 1:
            node = cls.__selection[0]
            if node.getBoundingBox() and node.getBoundingBox().isValid():
                return node.getBoundingBox().center
            else:
                return node.getWorldPosition()

        pos = Vector()
        for node in cls.__selection:
            if node.getBoundingBox() and node.getBoundingBox().isValid():
                pos += node.getBoundingBox().center
            else:
                pos += node.getWorldPosition()

        pos /= len(cls.__selection)

        return pos

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
    @classmethod
    def applyOperation(cls, operation, *args, **kwargs):
        if not cls.__selection:
            return

        op = None

        if len(cls.__selection) == 1:
            node = cls.__selection[0]
            op = operation(node, *args, **kwargs)
        else:
            op = GroupedOperation()

            for node in Selection.getAllSelectedObjects():
                op.addOperation(operation(node, *args, **kwargs))

        op.push()

    __selection = []
