import time
from unittest.mock import MagicMock

from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.OperationStack import OperationStack


def test_push():
    operation_stack = OperationStack(MagicMock())
    operation_stack.changed.emit = MagicMock()
    test_operation = GroupedOperation()

    test_operation_2 = GroupedOperation()

    operation_stack.push(test_operation)
    operation_stack.push(test_operation_2)

    # Since we added two operations that can be merged, we should end up with one operation!
    assert len(operation_stack.getOperations()) == 1

    test_operation_3 = GroupedOperation()

    # Fake call to notify the operation stack that the tool has stopped doing something
    operation_stack._onToolOperationStopped(None)
    # Pretend like another operation was added but with a lot of time in between.
    test_operation_3._timestamp = time.time() + 2000000
    operation_stack.push(test_operation_3)
    assert len(operation_stack.getOperations()) == 2

    operation_stack.undo()
    # The count should be at 4, since we added 3 operations and then undid the last one.
    assert operation_stack.changed.emit.call_count == 4
    operation_stack.undo()
    assert operation_stack.changed.emit.call_count == 5

    # There is nothing to undo!
    assert not operation_stack.canUndo()
    operation_stack.undo()
    assert operation_stack.changed.emit.call_count == 5

    operation_stack.redo()
    assert operation_stack.changed.emit.call_count == 6
    operation_stack.redo()
    assert operation_stack.changed.emit.call_count == 7
    assert not operation_stack.canRedo()