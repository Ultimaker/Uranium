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
    ({"label": "Test", "default_value": 1, "description": "Test Setting"}, {"label": "Test", "default_value": 1, "description": "Test Setting"}),
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "unit": "mm"}, {"unit": "mm"}),
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "value": "10" }, {"value": SettingFunction("10")}),
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
        "default_value": 10,
        "description": "Test Setting",
        "children": {
            "test_child_1": {
                "label": "Test Child 1",
                "default_value": 10,
                "description": "Test Child Setting 1"
            }
        }
    })

    assert len(definition.children) == 1
    assert len(definition.findChildren({ "key": "test_child_1" })) == 1
