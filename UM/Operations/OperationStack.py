import threading

class OperationStack:
    def __init__(self):
        self._operations = []
        self._current_index = -1
        self._lock = threading.Lock()

    def push(self, operation):
        self._lock.acquire()

        if self._current_index < len(self._operations) - 1:
            del self._operations[self._current_index + 1:len(self._operations)]

        self._operations.append(operation)
        operation.redo()
        self._current_index += 1

        self._doMerge()

        self._lock.release()

    def undo(self):
        self._lock.acquire()
        if self._current_index >= 0 and self._current_index < len(self._operations):
            self._operations[self._current_index].undo()
            self._current_index -= 1
        self._lock.release()

    def redo(self):
        self._lock.acquire()
        n = self._current_index + 1
        if n >= 0 and n < len(self._operations):
            self._operations[n].redo()
            self._current_index += 1
        self._lock.release()

    def getOperations(self):
        self._lock.acquire()
        return self._operations
        self._lock.release()

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
