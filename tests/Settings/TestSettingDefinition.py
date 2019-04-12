# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest

import UM.Settings.SettingDefinition
from UM.Settings.SettingFunction import SettingFunction


def test_create():
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)

    assert definition is not None
    assert definition.key == "test"
    assert definition.container is None


test_basic_properties_data = [
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "type": "int"}, {"label": "Test", "default_value": 1, "description": "Test Setting"}),
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "type": "int", "unit": "mm"}, {"unit": "mm"}),
    ({"label": "Test", "default_value": 1, "description": "Test Setting", "type": "int", "value": "10" }, {"value": SettingFunction("10")}),
]


@pytest.mark.parametrize("data,expected", test_basic_properties_data)
def test_basic_properties(data, expected):
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)

    definition.deserialize(data)

    for key, value in expected.items():
        assert getattr(definition, key) == value


def test_missing_properties():
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)

    with pytest.raises(AttributeError):
        definition.deserialize({})


def test_getAndSetAttr():
    # SettingDefinition overrides the __getattr_ and __setattr__, so we should also test a simple case.
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)

    definition.name = 12
    assert definition.name == 12

def test_getAndSetAttrUnknown():
    # SettingDefinition overrides the __getattr_ and __setattr__, but only for known properties.
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)

    with pytest.raises(AttributeError):
        definition.this_doesnt_exist

    with pytest.raises(NotImplementedError):
        definition.type = "ZOMG"


def test_children():
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)

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

    assert definition.isDescendant("test_child_1")

    child_1 = definition.getChild("test_child_1")
    assert child_1 is not None
    assert child_1.isAncestor("test")
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


toFloatConversionData = [
    ("12", 12),
    ("012", 12),
    ("12.1", 12.1),
    ("OMGZOMG", 0),
    ("-22", -22),
    ("012.9", 12.9)
]


@pytest.mark.parametrize("data,expected", toFloatConversionData)
def test_toFloatConversion(data, expected):
    assert UM.Settings.SettingDefinition._toFloatConversion(data) == expected

toIntConversionData = [
    ("12", 12),
    ("-2", -2),
    ("0", 0),
    ("01", 0)
]

@pytest.mark.parametrize("data,expected", toIntConversionData)
def test_toIntConversion(data, expected):
    assert UM.Settings.SettingDefinition._toIntConversion(data) == expected


def test_addSupportedProperty():
    UM.Settings.SettingDefinition.SettingDefinition.addSupportedProperty("test_name", "test_type", required = False, read_only = True)
    assert UM.Settings.SettingDefinition.SettingDefinition.hasProperty("test_name")
    assert UM.Settings.SettingDefinition.SettingDefinition.getPropertyType("test_name") == "test_type"
    assert UM.Settings.SettingDefinition.SettingDefinition.isReadOnlyProperty("test_name")
    assert not UM.Settings.SettingDefinition.SettingDefinition.isRequiredProperty("test_name")
    assert UM.Settings.SettingDefinition.SettingDefinition.dependsOnProperty("test_name") is None


def test_unknownProperty():
    assert not UM.Settings.SettingDefinition.SettingDefinition.hasProperty("NOPE")
    assert UM.Settings.SettingDefinition.SettingDefinition.getPropertyType("NOPE") is None
    assert not UM.Settings.SettingDefinition.SettingDefinition.isReadOnlyProperty("NOPE")
    assert not UM.Settings.SettingDefinition.SettingDefinition.isRequiredProperty("NOPE")
    assert UM.Settings.SettingDefinition.SettingDefinition.dependsOnProperty("NOPE") is None


def test_compare():
    definition = UM.Settings.SettingDefinition.SettingDefinition("test", None)
    definition_2 = UM.Settings.SettingDefinition.SettingDefinition("test2", None)
    assert definition == definition

    assert not definition == None
    assert not definition == 12
    assert not definition == definition_2