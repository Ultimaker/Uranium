from unittest.mock import MagicMock

import pytest

from UM.Settings.Models.SettingDefinitionsModel import SettingDefinitionsModel

test_validate_data = [
    {"attribute": "showAncestors", "value": True},
    {"attribute": "containerId", "value": "omg"},
    {"attribute": "showAll", "value": True},
    {"attribute": "visibilityHandler", "value": MagicMock()},
    {"attribute": "visibilityHandler", "value": MagicMock()}, # We want to set it twice so that the signals get disconnected
    {"attribute": "exclude", "value": ["yay"]},
    {"attribute": "expanded", "value": ["yay"]},
    {"attribute": "filter", "value": {}}
]

@pytest.mark.parametrize("data", test_validate_data)
def test_getAndSet(data):
    model = SettingDefinitionsModel()

    # Convert the first letter into a capital
    attribute = list(data["attribute"])
    attribute[0] = attribute[0].capitalize()
    attribute = "".join(attribute)

    # Attempt to set the value
    getattr(model, "set" + attribute)(data["value"])

    # Ensure that the value got set
    assert getattr(model, data["attribute"]) == data["value"]
