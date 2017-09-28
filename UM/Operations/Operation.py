# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import time

from UM.Application import Application


##  Base class for operations that should support undo and redo.
class Operation:
    def __init__(self):
        super().__init__()
        self._timestamp = time.time()
        self._always_merge = False

    ##  Undo the operation.
    #
    #   This should be reimplemented by subclasses to perform all actions necessary to
    #   redo the operation.
    def undo(self):
        raise NotImplementedError("Undo should be reimplemented by subclasses")

    ##  Redo the operation.
    #
    #   This should be reimplemented by subclasses to perform all actions necessary to
    #   redo the operation.
    #
    #   \note This is automatically called when the operation is first put onto the OperationStack.
    def redo(self):
        raise NotImplementedError("Redo should be reimplemented by subclasses")

    ##  Perform operation merging.
    #
    #   This will be called by OperationStack to perform merging of operations.
    #   If this operation can be merged with `other`, it should return a new operation that
    #   is the combination of this operation and `other`. If it cannot be merged, False should
    #   be returned.
    #
    #   \param other \type{Operation} The operation to merge with.
    #
    #   \return An operation when this operation and `other` can be merged, or False if they cannot be merged.
    def mergeWith(self, other):
        return False

    ##  Push the operation onto the stack.
    #
    #   This is a convenience method that pushes this operation onto the Application's
    #   operation stack.
    def push(self):
        Application.getInstance().getOperationStack().push(self)
