from . import Operation

class GroupedOperation(Operation.Operation):
    def __init__(self):
        super().__init__()
        self._children = []

    def addOperation(self, op):
        self._children.append(op)

    def removeOperation(self, index):
        del self._children[index]

    def undo(self):
        for op in self._children:
            op.undo()

    def redo(self):
        for op in self._children:
            op.redo()
