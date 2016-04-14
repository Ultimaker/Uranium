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
        self._finalised = False #Indicates if this operation is ever used. After that, it may no longer be modified.

    ##  Adds an operation to this group.
    #
    #   The operation will be undone together with the rest of the operations in
    #   this group.
    #   Note that when the order matters, the operations are undone in reverse
    #   order as the order in which they are added.
    def addOperation(self, op):
        if self._finalised:
            raise Exception("A grouped operation may not be modified after it is used.")
        self._children.append(op)

    ##  Undo all operations in this group.
    #
    #   The operations are undone in reverse order as the order in which they
    #   were added.
    def undo(self):
        for op in reversed(self._children):
            op.undo()
        self._finalised = True

    ##  Redoes all operations in this group.
    def redo(self):
        for op in self._children:
            op.redo()
        self._finalised = True