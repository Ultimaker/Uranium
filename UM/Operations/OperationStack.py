import threading

class OperationStack:
    def __init__(self):
        self._operations = []
        self._current_index = -1
        self._lock = threading.Lock()

    def push(self, operation):
        self._lock.acquire(True, 1)

        try:
            if self._current_index < len(self._operations) - 1:
                del self._operations[self._current_index + 1:len(self._operations)]

            self._operations.append(operation)
            operation.redo()
            self._current_index += 1

            self._doMerge()
        finally:
            self._lock.release()

    def undo(self):
        with self._lock:
            if self._current_index >= 0 and self._current_index < len(self._operations):
                self._operations[self._current_index].undo()
                self._current_index -= 1

    def redo(self):
        with self._lock:
            n = self._current_index + 1
            if n >= 0 and n < len(self._operations):
                self._operations[n].redo()
                self._current_index += 1

    def getOperations(self):
        with self._lock:
            return self._operations

    ## private:

    def _doMerge(self):
        if len(self._operations) >= 2:
            op1 = self._operations[self._current_index]
            op2 = self._operations[self._current_index - 1]

            merged = op1.mergeWith(op2)
            if merged:
                del self._operations[self._current_index]
                del self._operations[self._current_index - 1]
                self._current_index -= 1
                self._operations.append(merged)
