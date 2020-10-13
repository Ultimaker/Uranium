# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import time


class Operation:
    """Base class for operations that should support undo and redo."""

    def __init__(self) -> None:
        super().__init__()
        self._timestamp = time.time()
        self._always_merge = False

    def undo(self) -> None:
        """Undo the operation.

        This should be reimplemented by subclasses to perform all actions necessary to
        redo the operation.
        """

        raise NotImplementedError("Undo should be reimplemented by subclasses")

    def redo(self) -> None:
        """Redo the operation.

        This should be reimplemented by subclasses to perform all actions necessary to
        redo the operation.

        :note This is automatically called when the operation is first put onto the OperationStack.
        """

        raise NotImplementedError("Redo should be reimplemented by subclasses")

    def mergeWith(self, other):
        """Perform operation merging.

        This will be called by OperationStack to perform merging of operations.
        If this operation can be merged with `other`, it should return a new operation that
        is the combination of this operation and `other`. If it cannot be merged, False should
        be returned.

        :param other: :type{Operation} The operation to merge with.

        :return: An operation when this operation and `other` can be merged, or False if they cannot be merged.
        """

        return False

    def push(self) -> None:
        """Push the operation onto the stack.

        This is a convenience method that pushes this operation onto the Application's
        operation stack.
        """

        # Because of circular dependency
        from UM.Application import Application
        Application.getInstance().getOperationStack().push(self)
