from unittest.mock import MagicMock

import pytest

from UM.OutputDevice.OutputDevice import OutputDevice

test_validate_data = [
    {"attribute": "IconName", "value": "blarg"},
    {"attribute": "ShortDescription", "value": "omg"},
    {"attribute": "Name", "value": "SHeWhoShallNotBeNamed"},
    {"attribute": "Description", "value": "OH NOES!"},
    {"attribute": "Priority", "value": 12}
]


def test_createOutputDevice():
    output_device = OutputDevice("Random_id")
    assert output_device.getId() == "Random_id"


@pytest.mark.parametrize("data", test_validate_data)
def test_getAndSet(data):
    output_device = OutputDevice("Random_id")

    output_device.metaDataChanged = MagicMock()
    # Attempt to set the value
    getattr(output_device, "set" + data["attribute"])(data["value"])

    # Ensure that the value got set
    assert getattr(output_device, "get" + data["attribute"])() == data["value"]

    # Check if signal fired.
    assert output_device.metaDataChanged.emit.call_count == 1

    # Attempt to set the setter to the same value again.
    getattr(output_device, "set" + data["attribute"])(data["value"])
    # Ensure signal fired only once!
    assert output_device.metaDataChanged.emit.call_count == 1
