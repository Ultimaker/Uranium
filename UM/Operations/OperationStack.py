# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, SignalEmitter

import threading

##  A stack of operations
class OperationStack(SignalEmitter):
    def __init__(self):
        self._operations = []
        self._current_index = -1
        self._lock = threading.Lock()

    ##  Push an operation on the stack.
    #
    #   This will perform the follwing things in sequence:
    #   - If the current index is pointing to an item lower in the stack than the top,
    #     remove all operations from the current index to the top.
    #   - Append the operation to the stack.
    #   - Call redo() on the operation.
    #   - Perform merging of operations.
    #
    #   \param operation \type{Operation} The operation to push onto the stack.
    def push(self, operation):
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

    ##  Undo the current operation.
    #
    #   This will call undo() on the current operation and decrement the current index.
    def undo(self):
        with self._lock:
            if self._current_index >= 0 and self._current_index < len(self._operations):
                self._operations[self._current_index].undo()
                self._current_index -= 1
                self.changed.emit()

    ##  Redo the next operation.
    #
    #   This will call redo() on the current operation and increment the current index.
    def redo(self):
        with self._lock:
            n = self._current_index + 1
            if n >= 0 and n < len(self._operations):
                self._operations[n].redo()
                self._current_index += 1
                self.changed.emit()

    def getOperations(self):
        with self._lock:
            return self._operations

    def canUndo(self):
        return self._current_index >= 0

    def canRedo(self):
        return self._current_index < len(self._operations) - 1

    changed = Signal()

    ## private:

    def _doMerge(self):
        if len(self._operations) >= 2:
            op1 = self._operations[self._current_index]
            op2 = self._operations[self._current_index - 1]

            if not op1._always_merge and not op2._always_merge:
                if abs(op1._timestamp - op2._timestamp) > self._merge_window:
                    return

            merged = op1.mergeWith(op2)
            if merged:
                del self._operations[self._current_index]
                del self._operations[self._current_index - 1]
                self._current_index -= 1
                self._operations.append(merged)

    _merge_window = 1.0
