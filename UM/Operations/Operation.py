class Operation:
    def __init__(self):
        super().__init__()

    def undo(self):
        raise NotImplementedError("Undo should be reimplemented by subclasses")

    def redo(self):
        raise NotImplementedError("Redo should be reimplemented by subclasses")

    def mergeWith(self, other):
        pass
