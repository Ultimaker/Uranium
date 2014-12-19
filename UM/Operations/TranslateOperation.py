from . import Operation

class TranslateOperation(Operation.Operation):
    def __init__(self, node, translation):
        super().__init__()
        self._node = node
        self._translation = translation

    def undo(self):
        self._node.translate(-self._translation)

    def redo(self):
        self._node.translate(self._translation)
