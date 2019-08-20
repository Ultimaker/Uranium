from PyQt5.QtCore import QPoint

from UM.Qt.Bindings.PointingRectangle import PointingRectangle
import pytest
from unittest.mock import MagicMock


test_validate_data_get_set = [
    {"attribute": "arrowSize", "value": "YAY"},
    {"attribute": "color", "value": "zomg"},
    {"attribute": "borderWidth", "value": 12},
    {"attribute": "borderColor", "value": "zomg!"},
    {"attribute": "target", "value": "Yourself"}
]

@pytest.mark.parametrize("data", test_validate_data_get_set)
def test_getAndSet(data):
    model = PointingRectangle()

    # Convert the first letter into a capital
    attribute = list(data["attribute"])
    attribute[0] = attribute[0].capitalize()
    attribute = "".join(attribute)

    # mock the correct emit
    setattr(model, data["attribute"] + "Changed", MagicMock())

    # Attempt to set the value
    getattr(model, "set" + attribute)(data["value"])

    # Check if signal fired.
    signal = getattr(model, data["attribute"] + "Changed")
    assert signal.emit.call_count == 1

    # Ensure that the value got set
    assert getattr(model, data["attribute"]) == data["value"]

    # Attempt to set the value again
    getattr(model, "set" + attribute)(data["value"])
    # The signal should not fire again
    assert signal.emit.call_count == 1


@pytest.mark.parametrize("width,height,target,result_points", [(0, 0, None, [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]),
                                                               (100, 20, None, [(0, 0), (0, 20), (100, 20), (100, 0), (0, 0), (0, 0), (0, 0)]),
                                                               (100, 20, QPoint(300, 10), [(0, 0), (0, 20), (100, 20), (100, 0), (100, 0), (110, 10), (100, 20)]), # Arrow on the right
                                                                (100, 20, QPoint(100, 100), [(0, 0), (0, 20), (100, 20), (100, 0), (80, 20), (90, 30), (100, 20)]),  # Arrow on bottom
                                                                (100, 20, QPoint(100, -2), [(0, 0), (0, 20), (100, 20), (100, 0), (80, 0), (90, -10), (100, 0)]), # Arrow on top
                                                                (100, 20, QPoint(-1, 0), [(0, 0), (0, 20), (100, 20), (100, 0), (0, 0), (-10, 10), (0, 20)])  # Arrow on left
                                                               ])
def test_updatePaintNode(width, height, target, result_points):
    item = PointingRectangle()

    item.setWidth(width)
    item.setHeight(height)
    if target is not None:
        item.setTarget(target)
        item.setArrowSize(10)
    mocked_node = MagicMock()
    mocked_update_data = MagicMock()

    item.updatePaintNode(mocked_node, mocked_update_data)

    assert mocked_node.removeAllChildNodes.call_count == 1
    assert mocked_node.setGeometry.call_count == 1

    geometry = mocked_node.setGeometry.call_args_list[0][0][0]
    assert len(geometry.vertexDataAsPoint2D()) == 7

    for idx, point in enumerate(result_points):
        assert comparePoint2D(geometry.vertexDataAsPoint2D()[idx], point[0], point[1])


def comparePoint2D(point, x, y):
    return point.x == x and point.y == y


