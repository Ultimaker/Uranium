# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os

import UM.Settings

from UM.Resources import Resources
Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def container_registry():
    UM.Settings.ContainerRegistry._ContainerRegistry__instance = None
    UM.Settings.ContainerRegistry.getInstance().load()
    return UM.Settings.ContainerRegistry.getInstance()

def test_instance_container():
    container = UM.Settings.InstanceContainer("test")
    assert container.getId() == "test"

def test_advanced_setProperty():
    instance_container = UM.Settings.InstanceContainer("test")

    definition1 = UM.Settings.SettingDefinition("test_0", None)
    definition1.deserialize({
        "label": "Test 0",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0,
        "minimum": "test_1 / 10",
    })

    definition2 = UM.Settings.SettingDefinition("test_1", None)
    definition2.deserialize({
        "label": "Test 1",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 50.0,
        "value": "test_0 * 5",
        "maximum": "test_0 * 10"
    })

    # Manually set up relations between definition1 and definition2
    # Normally this would be taken care of by the DefinitionContainer
    definition1.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition1, target = definition2, relation_type = UM.Settings.SettingRelation.RelationType.RequiredByTarget, role = "value"))
    definition2.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition2, target = definition1, relation_type = UM.Settings.SettingRelation.RelationType.RequiresTarget, role = "value"))
    definition1.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition1, target = definition2, relation_type = UM.Settings.SettingRelation.RelationType.RequiredByTarget, role = "maximum"))
    definition2.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition2, target = definition1, relation_type = UM.Settings.SettingRelation.RelationType.RequiresTarget, role = "maximum"))
    definition1.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition1, target = definition2, relation_type = UM.Settings.SettingRelation.RelationType.RequiresTarget, role = "minimum"))
    definition2.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition2, target = definition1, relation_type = UM.Settings.SettingRelation.RelationType.RequiredByTarget, role = "minimum"))

    def1_instance = UM.Settings.SettingInstance(definition1, instance_container)
    instance_container.addInstance(def1_instance)
    def1_instance.setProperty("value", 20.0)

    assert def1_instance.value == 20.0
    assert def1_instance.minimum == 10.0

    with pytest.raises(AttributeError):
        assert def1_instance.maximum == 50.0

    def2_instance = instance_container.getInstance("test_1")
    assert def2_instance is not None
    assert def2_instance.value == 100
    assert def2_instance.maximum == 200

    with pytest.raises(AttributeError):
        assert def2_instance.minimum == 10.0

def test_serialize(container_registry):
    instance_container = UM.Settings.InstanceContainer("test")
    definition = container_registry.findDefinitionContainers(id = container_data["definition"])[0]
    instance_container.setDefinition(definition)

    result = instance_container.serialize()
    print(result)

    assert result == """[general]
version = 1
name = test
definition = basic

[metadata]

[values]

"""

test_deserialize_data = [
    ("basic.inst.cfg", {"name": "Test"}),
]
@pytest.mark.parametrize("filename,expected", test_deserialize_data)
def test_deserialize(filename, expected, container_registry):
    instance_container = UM.Settings.InstanceContainer(filename)

    path = Resources.getPath(Resources.InstanceContainers, filename)
    with open(path) as data:
        instance_container.deserialize(data.read())

    for key, value in expected.items():
        if key == "name":
            assert instance_container.getName() == value


