# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

import UM.Settings

from UM.Settings.SettingFunction import SettingFunction

def test_create():
    definition = UM.Settings.SettingDefinition("test", None)

    assert definition is not None
    assert definition.key is "test"
    assert definition.container is None


test_basic_properties_data = [
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "type": "int"}, {"label": "Test", "default_value": 1, "description": "Test Setting"}),
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "type": "int", "unit": "mm"}, {"unit": "mm"}),
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "type": "int", "value": "10" }, {"value": SettingFunction("10")}),
]
@pytest.mark.parametrize("data,expected", test_basic_properties_data)
def test_basic_properties(data, expected):
    definition = UM.Settings.SettingDefinition("test", None)

    definition.deserialize(data)

    for key, value in expected.items():
        assert getattr(definition, key) == value

def test_missing_properties():
    definition = UM.Settings.SettingDefinition("test", None)

    with pytest.raises(AttributeError):
        definition.deserialize({})

def test_children():
    definition = UM.Settings.SettingDefinition("test", None)

    definition.deserialize({
        "label": "Test",
        "type": "int",
        "default_value": 10,
        "description": "Test Setting",
        "children": {
            "test_child_1": {
                "label": "Test Child 1",
                "type": "int",
                "default_value": 20,
                "description": "Test Child Setting 1"
            },
            "test_child_2": {
                "label": "Test Child 2",
                "type": "int",
                "default_value": 20,
                "description": "Test Child Setting 2"
            }
        }
    })

    assert len(definition.children) == 2

    child_1 = definition.getChild("test_child_1")
    assert child_1 is not None
    assert child_1.key == "test_child_1"
    assert child_1.label == "Test Child 1"
    assert child_1.default_value == 20
    assert child_1.description == "Test Child Setting 1"

    definitions = definition.findDefinitions(default_value = 20)
    assert len(definitions) == 2

    has_child_1 = False
    has_child_2 = False
    for definition in definitions:
        if definition.key == "test_child_1":
            has_child_1 = True
        elif definition.key == "test_child_2":
            has_child_2 = True

    assert has_child_1
    assert has_child_2

