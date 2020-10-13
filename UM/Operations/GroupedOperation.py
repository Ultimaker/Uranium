# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import Operation
from typing import List


class GroupedOperation(Operation.Operation):
    """An operation that groups several other operations together.

    The intent of this operation is to hide an underlying chain of operations
    from the user if they correspond to only one interaction with the user, such
    as an operation applied to multiple scene nodes or a re-arrangement of
    multiple items in the scene.
    """

    def __init__(self) -> None:
        """Creates a new grouped operation.

        The grouped operation is empty after its initialisation.
        """

        super().__init__()
        self._children = []  # type: List[Operation.Operation]
        self._finalised = False  # Indicates if this operation is ever used. After that, it may no longer be modified.

    def getNumChildrenOperations(self) -> int:
        return len(self._children)

    def addOperation(self, op: Operation.Operation) -> None:
        """Adds an operation to this group.

        The operation will be undone together with the rest of the operations in
        this group.
        Note that when the order matters, the operations are undone in reverse
        order as the order in which they are added.
        """

        if self._finalised:
            raise Exception("A grouped operation may not be modified after it is used.")
        self._children.append(op)

    def undo(self) -> None:
        """Undo all operations in this group.

        The operations are undone in reverse order as the order in which they
        were added.
        """

        for op in reversed(self._children):
            op.undo()
        self._finalised = True

    def redo(self) -> None:
        """Redoes all operations in this group."""

        for op in self._children:
            op.redo()
        self._finalised = True

    def mergeWith(self, other):
        """Merges this operation with another GroupOperation.

        This prevents the user from having to undo multiple operations if they
        were not his operations.

        The older operation must have the same number of child operations, and
        each pair of operations must succesfully merge, or the merge of the
        groupOperation will fail.

        :param other: The older GroupOperation to merge this with.
        :return: A combination of the two group operations, or False if the operations
        can not be merged.
        """

        if type(other) is not GroupedOperation:
            return False
        if len(other._children) != len(self._children):  # Must be operations on the same number of children.
            return False

        op = GroupedOperation()
        for (op1, op2) in zip(self._children, other._children):
            child_op = op1.mergeWith(op2)
            if not child_op:
                return False
            op.addOperation(child_op)
        return op

    def __repr__(self):
        output = "GroupedOp.(#={0})\n".format(len(self._children))
        for child in self._children:
            output += "{0!r}\n".format(child)
        return output
