# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest

# import UM.Settings
import UM.Settings.SettingFunction
import UM.Settings.SettingDefinition
import UM.Settings.SettingInstance

from copy import deepcopy


##  A very basic copy of the instance container.
#
#   Since validator makes have use of this we need it to make validators work.
class MockContainer():
    def __init__(self):
        super().__init__()

        self._instances = []

    def getProperty(self, key, property_name, context = None):
        for instance in self._instances:
            if instance.definition.key == key:
                try:
                    value = getattr(instance, property_name)
                except AttributeError:
                    break

                if isinstance(value, UM.Settings.SettingFunction.SettingFunction):
                    return value(self)
                else:
                    return value

        return None

    def addInstance(self, instance):
        self._instances.append(instance)

    def isDirty(self):
        return True

@pytest.fixture
def setting_definition():
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)
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
    instance = UM.Settings.SettingInstance.SettingInstance(setting_definition, instance_container)

    assert instance.definition == setting_definition
    assert instance.container == instance_container

def test_setProperty(setting_definition, instance_container):
    instance = UM.Settings.SettingInstance.SettingInstance(setting_definition, instance_container)
    instance_container.addInstance(instance)

    instance.setProperty("value", 20.0)
    assert instance.value == 20.0
    assert instance.state == UM.Settings.SettingInstance.InstanceState.User
    assert instance.validationState(instance_container) == UM.Settings.Validator.ValidatorState.Valid

    with pytest.raises(AttributeError):
        instance.setProperty("something", 10)

test_validationState_data = [
    {"value": 10.0, "state": UM.Settings.Validator.ValidatorState.Valid},
    {"value": 4.0, "state": UM.Settings.Validator.ValidatorState.MinimumWarning},
    {"value": 19.0, "state": UM.Settings.Validator.ValidatorState.MaximumWarning},
    {"value": -1.0, "state": UM.Settings.Validator.ValidatorState.MinimumError},
    {"value": 33.0, "state": UM.Settings.Validator.ValidatorState.MaximumError},
]
@pytest.mark.parametrize("data", test_validationState_data)
def test_validationState(data, instance_container):
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)
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

    instance = UM.Settings.SettingInstance.SettingInstance(definition, instance_container)
    instance_container.addInstance(instance)

    # Ensure the instance is filled with proper values for the validation range
    instance.setProperty("minimum_value", 0.0)
    instance.setProperty("maximum_value", 20.0)
    instance.setProperty("minimum_value_warning", 5.0)
    instance.setProperty("maximum_value_warning", 15.0)

    instance.setProperty("value", data["value"])

    assert instance.validationState(instance_container) == data["state"]


def test_getNonExistingAttribute(setting_definition, instance_container):
    instance = UM.Settings.SettingInstance.SettingInstance(setting_definition, instance_container)

    with pytest.raises(AttributeError):
        instance.blarg


def test_compare(setting_definition, instance_container):
    instance = UM.Settings.SettingInstance.SettingInstance(setting_definition, instance_container)
    instance_container.addInstance(instance)
    assert instance != 12

    instance2 = deepcopy(instance)
    assert instance == instance2
    instance_container.addInstance(instance2)
    instance2.setProperty("maximum_value", 2000.0)

    # The direction should not matter (Before adding this test it did, so best to leave it in!)
    # In this case, we are testing instance 2 having the max_value property, but instance doesn't have it.
    assert instance2 != instance
    assert instance != instance2

    instance.setProperty("maximum_value", 9001)
    # In this case, we are testing instance 2 having the max_value property, but instance doesn't have it.
    assert instance2 != instance
    assert instance != instance2