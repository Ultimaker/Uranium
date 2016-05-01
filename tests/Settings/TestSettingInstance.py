# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

import UM.Settings

class MockContainer():
    def getValue(self, key): # Called by SettingInstance::updateProperty
        return 10.0

@pytest.fixture
def setting_definition():
    definition = UM.Settings.SettingDefinition("test", None)
    definition.deserialize({
        "label": "Test",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0,
        "maximum": "mock_test * 10"
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

    with pytest.raises(AttributeError):
        instance.setProperty("something", 10)

def test_updateProperty(setting_definition, instance_container):
    instance = UM.Settings.SettingInstance(setting_definition, instance_container)

    instance.updateProperty("maximum")

    assert instance.maximum == 100
