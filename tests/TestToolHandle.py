from unittest.mock import patch

import pytest

from UM.Scene.ToolHandle import ToolHandle

test_validate_data = [
    {"attribute": "LineMesh", "value": "whatever"},
    {"attribute": "SolidMesh", "value": "blorp"},
    {"attribute": "SelectionMesh", "value": "omgzomg"}
]

@pytest.mark.parametrize("data", test_validate_data)
def test_getAndSet(data):
    with patch("UM.Application.Application.getInstance"):
        tool_handle = ToolHandle()

    # Attempt to set the value
    getattr(tool_handle, "set" + data["attribute"])(data["value"])

    # Ensure that the value got set
    assert getattr(tool_handle, "get" + data["attribute"])() == data["value"]
