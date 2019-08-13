from UM.Settings.Models.InstanceContainersModel import InstanceContainersModel
from unittest.mock import MagicMock, patch
import pytest

@pytest.fixture
def instance_containers_model(container_registry):
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance",
               MagicMock(return_value=container_registry)):
        result = InstanceContainersModel()
        result._fetchInstanceContainers = MagicMock(return_value = ({}, {"bla": {"name": "test", "id": "beep"}}))
        return result


def test_simpleUpdate(instance_containers_model):
        instance_containers_model._update()
        items = instance_containers_model.items
        assert len(items) == 1
        assert items[0]["name"] == "test"
        assert items[0]["id"] == "beep"


test_validate_data_get_set = [
    {"attribute": "sectionProperty", "value": "YAY"},
    {"attribute": "filter", "value": {"beep": "oh noes"}},
]

@pytest.mark.parametrize("data", test_validate_data_get_set)
def test_getAndSet(data, instance_containers_model):
    model = instance_containers_model

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

