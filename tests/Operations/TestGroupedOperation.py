from unittest.mock import MagicMock

from UM.Math.Vector import Vector
from UM.Operations.GroupedOperation import GroupedOperation
import pytest

from UM.Operations.Operation import Operation
from UM.Operations.TranslateOperation import TranslateOperation
from UM.Scene.SceneNode import SceneNode


def test_addOperationFinalised():
    operation_1 = GroupedOperation()
    operation_2 = GroupedOperation()

    operation_1.redo()  # The operation is now finalized, so it shouldn't be possible to add operations to it now.
    with pytest.raises(Exception):
        operation_1.addOperation(operation_2)


def test_addAndMergeOperations():
    group_operation_1 = GroupedOperation()
    group_operation_2 = GroupedOperation()
    group_operation_3 = GroupedOperation()

    scene_node = SceneNode()

    operation_1 = TranslateOperation(scene_node, Vector(10, 10))
    operation_2 = TranslateOperation(scene_node, Vector(10, 20))
    operation_3 = Operation()

    operation_1.mergeWith = MagicMock()

    group_operation_1.addOperation(operation_1)
    assert group_operation_1.getNumChildrenOperations() == 1

    # Length of the grouped operations must be the same.
    assert not group_operation_1.mergeWith(group_operation_2)

    group_operation_3.addOperation(operation_3)

    # The base operation always says it can't be merged (so one child says it can't be merged). This should result
    # in the parent (grouped) operation also failing.
    assert not group_operation_3.mergeWith(group_operation_1)

    group_operation_2.addOperation(operation_2)
    merged_operation = group_operation_1.mergeWith(group_operation_2)

    # The merge of the nested operation should have been called once.
    assert operation_1.mergeWith.call_count == 1

    # Number of operations should still be the same.
    assert merged_operation.getNumChildrenOperations() == 1