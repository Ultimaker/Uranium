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

def test_create():
    container = UM.Settings.InstanceContainer("test")
    assert container.getId() == "test"

##  Test whether setting a property on an instance correctly updates dependencies.
#
#   This test primarily tests the SettingInstance but requires some functionality
#   from InstanceContainer that is not easily captured in a Mock object. Therefore
#   it is included here.
def test_instance_setProperty():
    instance_container = UM.Settings.InstanceContainer("test")

    definition1 = UM.Settings.SettingDefinition("test_0", None)
    definition1.deserialize({
        "label": "Test 0",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0,
        "minimum_value": "test_1 / 10",
    })

    definition2 = UM.Settings.SettingDefinition("test_1", None)
    definition2.deserialize({
        "label": "Test 1",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 50.0,
        "value": "test_0 * 5",
        "maximum_value": "test_0 * 10"
    })

    # Manually set up relations between definition1 and definition2
    # Normally this would be taken care of by the DefinitionContainer
    definition1.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition1, target = definition2, relation_type = UM.Settings.SettingRelation.RelationType.RequiredByTarget, role = "value"))
    definition2.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition2, target = definition1, relation_type = UM.Settings.SettingRelation.RelationType.RequiresTarget, role = "value"))
    definition1.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition1, target = definition2, relation_type = UM.Settings.SettingRelation.RelationType.RequiredByTarget, role = "maximum_value"))
    definition2.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition2, target = definition1, relation_type = UM.Settings.SettingRelation.RelationType.RequiresTarget, role = "maximum_value"))
    definition1.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition1, target = definition2, relation_type = UM.Settings.SettingRelation.RelationType.RequiresTarget, role = "minimum_value"))
    definition2.relations.append(UM.Settings.SettingRelation.SettingRelation(owner = definition2, target = definition1, relation_type = UM.Settings.SettingRelation.RelationType.RequiredByTarget, role = "minimum_value"))

    def1_instance = UM.Settings.SettingInstance(definition1, instance_container)
    instance_container.addInstance(def1_instance)
    def1_instance.setProperty("value", 20.0)

    assert def1_instance.value == 20.0

    with pytest.raises(AttributeError):
        assert def1_instance.maximum == 50.0

    assert definition2.value(instance_container) == 100
    assert definition2.maximum_value(instance_container) == 200

test_serialize_data = [
    ({"definition": "basic", "name": "Basic"}, "basic.inst.cfg"),
    ({"definition": "basic", "name": "Metadata", "metadata": {"author": "Ultimaker", "bool": False, "integer": 6 }}, "metadata.inst.cfg"),
    ({"definition": "multiple_settings", "name": "Setting Values", "values": {
        "test_setting_0": 20, "test_setting_1": 20, "test_setting_2": 20, "test_setting_3": 20, "test_setting_4": 20
    }}, "setting_values.inst.cfg"),
]
@pytest.mark.parametrize("container_data,equals_file", test_serialize_data)
def test_serialize(container_data, equals_file, container_registry):
    instance_container = UM.Settings.InstanceContainer("test")
    definition = container_registry.findDefinitionContainers(id = container_data["definition"])[0]
    instance_container.setDefinition(definition)

    instance_container.setName(container_data["name"])

    if "metadata" in container_data:
        instance_container.setMetaData(container_data["metadata"])

    if "values" in container_data:
        for key, value in container_data["values"].items():
            instance_container.setProperty(key, "value", value)

    result = instance_container.serialize()

    path = Resources.getPath(Resources.InstanceContainers, equals_file)
    with open(path) as data:
        assert data.readline() in result

test_deserialize_data = [
    ("basic.inst.cfg", {"name": "Basic"}),
    ("metadata.inst.cfg", {"name": "Metadata", "metaData": { "author": "Ultimaker", "bool": "False", "integer": "6" } }),
    ("setting_values.inst.cfg", {"name": "Setting Values", "values": { "test_setting_0": 20 } }),
]
@pytest.mark.parametrize("filename,expected", test_deserialize_data)
def test_deserialize(filename, expected, container_registry):
    instance_container = UM.Settings.InstanceContainer(filename)

    path = Resources.getPath(Resources.InstanceContainers, filename)
    with open(path) as data:
        instance_container.deserialize(data.read())

    for key, value in expected.items():
        if key != "values":
            assert getattr(instance_container, key) == value
            continue

        for key, value in value.items():
            assert instance_container.getProperty(key, "value") == value

