class OperationStack:
    def __init__(self):
        self._operations = []
        self._current_index = -1

    def push(self, operation):
        if self._current_index == len(self._operations) - 1:
            self._current_index += 1

        self._operations.append(operation)
        operation.redo()

    def undo(self):
        if self._current_index >= 0 and self._current_index < len(self._operations):
            self._operations[self._current_index].undo()
            self._current_index -= 1

    def redo(self):
        n = self._current_index + 1
        if n >= 0 and n < len(self._operations):
            self._operations[n].redo()
            self._current_index += 1

    def getOperations(self):
        return self._operations
