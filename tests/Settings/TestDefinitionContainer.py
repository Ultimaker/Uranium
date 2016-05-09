# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path
import json
import collections
import uuid

import UM.Settings
from UM.Resources import Resources

Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))

##  A fixture to create new definition containers with.
#
#   The container will have a unique ID.
@pytest.fixture
def definition_container():
    return UM.Settings.DefinitionContainer(uuid.uuid4().int)

test_definition_container_data = [
    ("basic.def.json", { "name": "Test", "metadata": {}, "settings": {} }),
    ("metadata.def.json", { "name": "Test", "metadata": { "author": "Ultimaker", "category": "Test" }, "settings": {} }),
    ("single_setting.def.json", { "name": "Test", "metadata": {}, "settings": { "test_setting": { "label": "Test", "default_value": 10, "description": "A Test Setting" } } }),
    ("multiple_settings.def.json", { "name": "Test", "metadata": {}, "settings": {
        "test_setting_0": { "label": "Test 0", "default_value": 10, "description": "A Test Setting" },
        "test_setting_1": { "label": "Test 1", "default_value": 10, "description": "A Test Setting" },
        "test_setting_2": { "label": "Test 2", "default_value": 10, "description": "A Test Setting" },
        "test_setting_3": { "label": "Test 3", "default_value": 10, "description": "A Test Setting" },
        "test_setting_4": { "label": "Test 4", "default_value": 10, "description": "A Test Setting" }
    }}),
    ("children.def.json", { "name": "Test", "metadata": {}, "settings": {
        "test_setting": { "label": "Test", "default_value": 10, "description": "A Test Setting"},
        "test_child_0": { "label": "Test Child 0", "default_value": 10, "description": "A Test Setting"},
        "test_child_1": { "label": "Test Child 1", "default_value": 10, "description": "A Test Setting"},
    }}),
    ("inherits.def.json", { "name": "Inherits", "metadata": {"author": "Ultimaker", "category": "Other", "manufacturer": "Ultimaker" }, "settings": {
        "test_setting": { "label": "Test", "default_value": 10, "description": "A Test Setting" },
        "test_setting_1": { "label": "Test 1", "default_value": 10, "description": "A Test Setting" },
    }}),
    ("functions.def.json", { "name": "Test", "metadata": {}, "settings": {
        "test_setting_0": { "label": "Test 0", "default_value": 10, "description": "A Test Setting" },
        "test_setting_1": { "label": "Test 1", "default_value": 10, "description": "A Test Setting", "value": UM.Settings.SettingFunction.SettingFunction("test_setting_0 * 10") },
    }})
]
@pytest.mark.parametrize("file,expected", test_definition_container_data)
def test_definition_container(file, expected):
    container = UM.Settings.DefinitionContainer("test")
    assert container.getId() == "test"

    json = ""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)) as data:
        json = data.read()

    container.deserialize(json)

    assert container.getName() == expected["name"]

    for key, value in expected["metadata"].items():
        assert container.getMetaDataEntry(key) == value

    for key, value in expected["settings"].items():
        settings = container.findDefinitions(key = key)

        assert len(settings) == 1

        setting = settings[0]
        assert setting.key == key

        for property, property_value in value.items():
            assert getattr(setting, property) == property_value

##  Tests getting metadata entries.
#
#   \param definition_container A new definition container from a fixture.
def test_getMetaDataEntry(definition_container):
    metadata = definition_container.getMetaData()

    metadata["foo"] = "bar" # Normal case.
    assert definition_container.getMetaDataEntry("foo") == "bar"

    assert definition_container.getMetaDataEntry("zoo", 42) == 42 # Non-existent entry must return the default.

def test_setting_function():
    container = UM.Settings.DefinitionContainer("test")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", "functions.def.json")) as data:
        container.deserialize(data.read())

    setting_0 = container.findDefinitions(key = "test_setting_0")[0]
    setting_1 = container.findDefinitions(key = "test_setting_1")[0]

    function = setting_1.value

    assert len(setting_0.relations) == 1
    assert len(setting_1.relations) == 1

    relation_0 = setting_0.relations[0]
    relation_1 = setting_1.relations[0]

    assert relation_0.owner == setting_0
    assert relation_0.target == setting_1
    assert relation_0.type == UM.Settings.SettingRelation.RelationType.RequiredByTarget
    assert relation_0.role == "value"

    assert relation_1.owner == setting_1
    assert relation_1.target == setting_0
    assert relation_1.type == UM.Settings.SettingRelation.RelationType.RequiresTarget
    assert relation_1.role == "value"

    assert isinstance(function, UM.Settings.SettingFunction.SettingFunction)

    result = function(container)
    assert result == (setting_0.default_value * 10)