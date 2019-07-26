from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.Models.ContainerPropertyProvider import ContainerPropertyProvider
import pytest
from unittest.mock import patch, MagicMock


test_validate_data_get_set = [
    {"attribute": "containerId", "value": "YAY"},
    {"attribute": "watchedProperties", "value": {"beep": "oh noes"}},
    {"attribute": "key", "value": "YAY"},
]

@pytest.fixture()
def registry():
    mocked_registry = MagicMock()
    mocked_registry.isReadOnly = MagicMock(return_value=False)
    mocked_container = MagicMock()
    mocked_container.getProperty = MagicMock(return_value = "yay")
    mocked_registry.findContainers = MagicMock(return_value = [mocked_container])
    return mocked_registry


@pytest.mark.parametrize("data", test_validate_data_get_set)
def test_getAndSet(data):
    model = ContainerPropertyProvider()

    # Convert the first letter into a capital
    attribute = list(data["attribute"])
    attribute[0] = attribute[0].capitalize()
    attribute = "".join(attribute)

    # mock the correct emit
    setattr(model, data["attribute"] + "Changed", MagicMock())

    # Attempt to set the value
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance"):
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


def test_setPropertyValueNoKey(registry):
    model = ContainerPropertyProvider()
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", MagicMock(return_value = registry)):
        model.setContainerId("bloop")
        model.setPropertyValue("derp", "zomg")
        # Check if the mocked container got it's setProperty targeted
        assert ContainerRegistry.getInstance().findContainers()[0].setProperty.call_count == 0


def test_setPropertyValueNotWatchedProperty(registry):
    model = ContainerPropertyProvider()
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", MagicMock(return_value = registry)):
        model.setContainerId("bloop")
        model.setKey("whatever")
        model.setPropertyValue("derp", "zomg")
        # Check if the mocked container got it's setProperty targeted
        assert ContainerRegistry.getInstance().findContainers()[0].setProperty.call_count == 0

def test_setPropertyValue(registry):
    model = ContainerPropertyProvider()
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", MagicMock(return_value = registry)):
        model.setContainerId("bloop")
        model.setWatchedProperties(["derp"])
        model.setKey("whatever")
        model.setPropertyValue("derp", "zomg")
        # Check if the mocked container got it's setProperty targeted
        assert ContainerRegistry.getInstance().findContainers()[0].setProperty.call_count == 1


def test_setPropertyValueCache(registry):
    model = ContainerPropertyProvider()
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", MagicMock(return_value=registry)):
        model.setContainerId("bloop")
        model.setWatchedProperties(["derp", "yay"])
        model.setKey("derp")
        # Fake that we got a signal indicating the value is already set
        model._onPropertyChanged("derp", "yay")

        model.setPropertyValue("derp", "yay")

        # Check if the mocked container got it's setProperty targeted
        assert ContainerRegistry.getInstance().findContainers()[0].setProperty.call_count == 0
