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

    def mergeWith(self, other):
        if type(other) is not TranslateOperation:
            return False

        if other._node != self._node:
            return False

        if self._timestamp - other._timestamp > self._mergeWindow:
            return False

        return TranslateOperation(self._node, self._translation + other._translation)

    def __repr__(self):
        return "TranslateOperation(node = {0}, translation={1})".format(self._node, self._translation)

    ## private:

    _mergeWindow = 0.5 #If the time between this operation and a different operation is less than this they can be merged.
