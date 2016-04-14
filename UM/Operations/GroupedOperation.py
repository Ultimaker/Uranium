# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

##  An operation that groups several other operations together.
#
#   The intent of this operation is to hide an underlying chain of operations
#   from the user if they correspond to only one interaction with the user, such
#   as an operation applied to multiple scene nodes or a re-arrangement of
#   multiple items in the scene.
class GroupedOperation(Operation.Operation):
    ##  Creates a new grouped operation.
    #
    #   The grouped operation is empty after its initialisation.
    def __init__(self):
        super().__init__()
        self._children = []

    ##  Adds an operation to this group.
    #
    #   The operation will be undone together with the rest of the operations in
    #   this group.
    def addOperation(self, op):
        self._children.append(op)

    ##  Removes an operation from this group.
    def removeOperation(self, index):
        del self._children[index]

    ##  Undo all operations in this group.
    def undo(self):
        for op in self._children:
            op.undo()

    ##  Redoes all operations in this group.
    def redo(self):
        for op in self._children:
            op.redo()
