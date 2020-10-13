# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import threading
import time

from UM.Logger import Logger
from UM.Operations.Operation import Operation
from UM.Signal import Signal, signalemitter

from typing import List


@signalemitter
class OperationStack():
    """A stack of operations.

    This maintains the history of operations, which allows for undoing and
    re-doing these operations.
    """

    def __init__(self, controller) -> None:
        self._operations = []  # type: List[Operation]
        self._current_index = -1 #Index of the most recently executed operation.
        self._lock = threading.Lock() #Lock to make sure only one thread can modify the operation stack at a time.

        # The merge behaviour must only occur when an operation is in the middle of a user action.
        # So, whenever an operation is started or ended, we do not want this auto-merge.
        self._merge_operations = False
        self._controller = controller
        self._controller.toolOperationStarted.connect(self._onToolOperationStarted)
        self._controller.toolOperationStopped.connect(self._onToolOperationStopped)

    def _onToolOperationStarted(self, tool):
        self._merge_operations = False

    def _onToolOperationStopped(self, tool):
        self._merge_operations = False

    def push(self, operation):
        """Push an operation on the stack.

        This will perform the following things in sequence:
        - If the current index is pointing to an item lower in the stack than
        the top, remove all operations from the current index to the top.
        - Append the operation to the stack.
        - Call redo() on the operation.
        - Perform merging of operations.

        :param operation: :type{Operation} The operation to push onto the stack.
        """

        start_time = time.time()
        if not self._lock.acquire(False):
            return

        try:
            if self._current_index < len(self._operations) - 1:
                del self._operations[self._current_index + 1:len(self._operations)]

            self._operations.append(operation)
            operation.redo()
            self._current_index += 1

            self._doMerge()

            self.changed.emit()
        finally:
            self._lock.release()
        elapsed_time = time.time() - start_time

        Logger.log("d", " ".join(repr(operation).splitlines()) + ", took {0}ms".format(int(elapsed_time * 1000))) #Don't remove; used in regression-tests.

    def undo(self):
        """Undo the current operation.

        This will call undo() on the current operation and decrement the current index.
        """

        with self._lock:
            if self._current_index >= 0 and self._current_index < len(self._operations):
                self._operations[self._current_index].undo()
                self._current_index -= 1
                self.changed.emit()

    def redo(self):
        """Redo the next operation.

        This will call redo() on the current operation and increment the current index.
        """

        with self._lock:
            n = self._current_index + 1
            if n >= 0 and n < len(self._operations):
                self._operations[n].redo()
                self._current_index += 1
                self.changed.emit()

    def getOperations(self):
        """Get the list of operations in the stack.

        The end of the list represents the more recent operations.

        :return: A list of the operations on the stack, in order.
        """

        with self._lock:
            return self._operations

    def canUndo(self):
        """Whether we can undo any more operations.

        :return: True if we can undo any more operations, or False otherwise.
        """

        return self._current_index >= 0

    def canRedo(self):
        """Whether we can redo any more operations.

        :return: True if we can redo any more operations, or False otherwise.
        """

        return self._current_index < len(self._operations) - 1

    changed = Signal()
    """Signal for when the operation stack changes."""

    def _doMerge(self):
        """Merges two operations at the current position in the stack.

        This merges the "most recent" operation with the one before it. The
        "most recent" operation is the one that would be undone if the user
        would trigger an undo, i.e. the one at _current_index.
        """

        if len(self._operations) >= 2:
            op1 = self._operations[self._current_index]
            op2 = self._operations[self._current_index - 1]

            if not op1._always_merge and not op2._always_merge and not self._merge_operations:
                if abs(op1._timestamp - op2._timestamp) > self._merge_window: #For normal operations, only merge if the operations were very quickly after each other.
                    return

            self._merge_operations = True #A signal sets this to False again.
            merged = op1.mergeWith(op2)
            if merged: #Replace the merged operations in the stack with the new one.
                del self._operations[self._current_index]
                del self._operations[self._current_index - 1]
                self._current_index -= 1
                self._operations.append(merged)

    _merge_window = 1.0 #Don't merge operations that were longer than this amount of seconds apart.
