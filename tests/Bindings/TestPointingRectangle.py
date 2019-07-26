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