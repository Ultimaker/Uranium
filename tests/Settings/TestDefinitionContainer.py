# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path
import json
import collections

import UM.Settings

##  Custom subclass that overrides _loadFile so we search for files in test directories instead of resources.
class CustomDefinitionContainer(UM.Settings.DefinitionContainer):
    def _loadFile(self, file_name):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file_name + ".json")
        contents = {}
        with open(path) as f:
            contents = json.load(f, object_pairs_hook=collections.OrderedDict)
        return contents

test_definition_container_data = [
    ("basic.json", { "name": "Test", "metadata": {}, "settings": {} }),
    ("metadata.json", { "name": "Test", "metadata": { "author": "Ultimaker", "category": "Test" }, "settings": {} }),
    ("single_setting.json", { "name": "Test", "metadata": {}, "settings": { "test_setting": { "label": "Test", "default_value": 10, "description": "A Test Setting" } } }),
    ("multiple_settings.json", { "name": "Test", "metadata": {}, "settings": {
        "test_setting_0": { "label": "Test 0", "default_value": 10, "description": "A Test Setting" },
        "test_setting_1": { "label": "Test 1", "default_value": 10, "description": "A Test Setting" },
        "test_setting_2": { "label": "Test 2", "default_value": 10, "description": "A Test Setting" },
        "test_setting_3": { "label": "Test 3", "default_value": 10, "description": "A Test Setting" },
        "test_setting_4": { "label": "Test 4", "default_value": 10, "description": "A Test Setting" }
    }}),
    ("children.json", { "name": "Test", "metadata": {}, "settings": {
        "test_setting": { "label": "Test", "default_value": 10, "description": "A Test Setting"},
        "test_child_0": { "label": "Test Child 0", "default_value": 10, "description": "A Test Setting"},
        "test_child_1": { "label": "Test Child 1", "default_value": 10, "description": "A Test Setting"},
    }}),
    ("inherits.json", { "name": "Inherits", "metadata": {"author": "Ultimaker", "category": "Other", "manufacturer": "Ultimaker" }, "settings": {
        "test_setting": { "label": "Test", "default_value": 10, "description": "A Test Setting" },
        "test_setting_1": { "label": "Test 1", "default_value": 10, "description": "A Test Setting" },
    }})
]
@pytest.mark.parametrize("file,expected", test_definition_container_data)
def test_definition_container(file, expected):
    container = CustomDefinitionContainer("test")
    assert container.getId() == "test"

    json = ""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)) as data:
        json = data.read()

    container.deserialize(json)

    assert container.getName() == expected["name"]

    for key, value in expected["metadata"].items():
        assert container.getMetaDataEntry(key) == value

    for key, value in expected["settings"].items():
        settings = container.findDefinitions({"key": key})

        assert len(settings) == 1

        setting = settings[0]
        assert setting.key == key

        for property, property_value in value.items():
            assert getattr(setting, property) == property_value

