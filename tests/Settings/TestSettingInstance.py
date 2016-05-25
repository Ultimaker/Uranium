# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

import UM.Settings

class MockContainer():
    def getProperty(self, key, property_name): # Called by SettingInstance::updateProperty
        return 10.0

@pytest.fixture
def setting_definition():
    definition = UM.Settings.SettingDefinition("test", None)
    definition.deserialize({
        "label": "Test",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0,
        "maximum_value": "mock_test * 10"
    })
    return definition

@pytest.fixture
def instance_container():
    return MockContainer()

def test_create(setting_definition, instance_container):
    instance = UM.Settings.SettingInstance(setting_definition, instance_container)

    assert instance.definition == setting_definition
    assert instance.container == instance_container

def test_setProperty(setting_definition, instance_container):
    instance = UM.Settings.SettingInstance(setting_definition, instance_container)

    instance.setProperty("value", 20.0)
    assert instance.value == 20.0
    assert instance.state == UM.Settings.InstanceState.User
    assert instance.validationState == UM.Settings.ValidatorState.Valid

    with pytest.raises(AttributeError):
        instance.setProperty("something", 10)

def test_updateProperty(setting_definition, instance_container):
    instance = UM.Settings.SettingInstance(setting_definition, instance_container)

    instance.updateProperty("maximum_value")

    assert instance.maximum_value == 100
    # We are updating a property that is not value, so state should not change.
    assert instance.state == UM.Settings.InstanceState.Default

    # Since we only update maximum_value, value will not be set and validation will have nothing to validate
    assert instance.validationState == UM.Settings.ValidatorState.Unknown

test_validationState_data = [
    {"value": 10.0, "state": UM.Settings.ValidatorState.Valid},
    {"value": 4.0, "state": UM.Settings.ValidatorState.MinimumWarning},
    {"value": 19.0, "state": UM.Settings.ValidatorState.MaximumWarning},
    {"value": -1.0, "state": UM.Settings.ValidatorState.MinimumError},
    {"value": 33.0, "state": UM.Settings.ValidatorState.MaximumError},
]
@pytest.mark.parametrize("data", test_validationState_data)
def test_validationState(data, instance_container):
    definition = UM.Settings.SettingDefinition("test", None)
    definition.deserialize({
        "label": "Test",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0,
        "minimum_value": "0.0",
        "maximum_value": "20.0",
        "minimum_value_warning": "5.0",
        "maximum_value_warning": "15.0",
    })

    instance = UM.Settings.SettingInstance(definition, instance_container)

    # Ensure the instance is filled with proper values for the validation range
    instance.updateProperty("minimum_value")
    instance.updateProperty("maximum_value")
    instance.updateProperty("minimum_value_warning")
    instance.updateProperty("maximum_value_warning")

    instance.setProperty("value", data["value"])

    assert instance.validationState == data["state"]
