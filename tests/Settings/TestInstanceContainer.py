# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import unittest.mock #For MagicMock and patch.
import pytest
import os

import UM.Settings.InstanceContainer
import UM.Settings.SettingInstance
import UM.Settings.SettingDefinition
import UM.Settings.SettingRelation
from UM.Resources import Resources
import copy
from unittest.mock import MagicMock
Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))


def test_create():
    container = UM.Settings.InstanceContainer.InstanceContainer("test")
    assert container.getId() == "test"


##  Test whether setting a property on an instance correctly updates dependencies.
#
#   This test primarily tests the SettingInstance but requires some functionality
#   from InstanceContainer that is not easily captured in a Mock object. Therefore
#   it is included here.
def test_instance_setProperty():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")

    definition1 = UM.Settings.SettingDefinition.SettingDefinition("test_0", None)
    definition1.deserialize({
        "label": "Test 0",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0,
        "minimum_value": "test_1 / 10",
    })

    definition2 = UM.Settings.SettingDefinition.SettingDefinition("test_1", None)
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

    def1_instance = UM.Settings.SettingInstance.SettingInstance(definition1, instance_container)
    instance_container.addInstance(def1_instance)
    def1_instance.setProperty("value", 20.0)

    assert def1_instance.value == 20.0

    with pytest.raises(AttributeError):
        assert def1_instance.maximum == 50.0

    assert definition2.value(instance_container) == 100
    assert definition2.maximum_value(instance_container) == 200


test_serialize_data = [
    ({"definition": "basic_definition", "name": "Basic"}, "basic_instance.inst.cfg"),
    ({"definition": "basic_definition", "name": "Metadata", "metadata": {"author": "Ultimaker", "bool": False, "integer": 6}}, "metadata_instance.inst.cfg"),
    ({"definition": "multiple_settings", "name": "Setting Values", "values": {
        "test_setting_0": 20, "test_setting_1": 20, "test_setting_2": 20, "test_setting_3": 20, "test_setting_4": 20
    }}, "setting_values.inst.cfg"),
]


@pytest.mark.parametrize("container_data,equals_file", test_serialize_data)
def test_serialize(container_data, equals_file, loaded_container_registry):
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")

    if "metadata" in container_data:
        instance_container.setMetaData(container_data["metadata"])
    instance_container.setDefinition(container_data["definition"])
    instance_container.setName(container_data["name"])

    if "values" in container_data:
        for key, value in container_data["values"].items():
            instance_container.setProperty(key, "value", value)

    with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", unittest.mock.MagicMock(return_value = loaded_container_registry)):
        result = instance_container.serialize()

    path = Resources.getPath(Resources.InstanceContainers, equals_file)
    with open(path, encoding = "utf-8") as data:
        assert data.readline() in result


test_serialize_with_ignored_metadata_keys_data = [
    ({"definition": "basic_definition", "name": "Basic", "metadata": {"secret": "something", "secret2": "something2"}}, "basic_instance.inst.cfg"),
    ({"definition": "basic_definition", "name": "Metadata", "metadata": {"author": "Ultimaker", "bool": False, "integer": 6, "secret": "something", "secret2": "something2"}}, "metadata_instance.inst.cfg"),
    ({"definition": "multiple_settings", "name": "Setting Values",
      "metadata": {"secret": "something", "secret2": "something2"},
      "values": {
        "test_setting_0": 20, "test_setting_1": 20, "test_setting_2": 20, "test_setting_3": 20, "test_setting_4": 20
      }}, "setting_values.inst.cfg"),
]


@pytest.mark.parametrize("container_data,equals_file", test_serialize_with_ignored_metadata_keys_data)
def test_serialize_with_ignored_metadata_keys(container_data, equals_file, loaded_container_registry):
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")

    if "metadata" in container_data:
        instance_container.setMetaData(container_data["metadata"])
    instance_container.setName(container_data["name"])
    instance_container.setDefinition(container_data["definition"])

    if "values" in container_data:
        for key, value in container_data["values"].items():
            instance_container.setProperty(key, "value", value)

    ignored_metadata_keys = {"secret", "secret2"}
    with unittest.mock.patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", unittest.mock.MagicMock(return_value = loaded_container_registry)):
        result = instance_container.serialize(ignored_metadata_keys = ignored_metadata_keys)

    instance_container.deserialize(result)
    new_metadata = instance_container.getMetaData()

    # the ignored keys should not be in the serialised metadata
    for key in ignored_metadata_keys:
        assert key not in new_metadata


test_deserialize_data = [
    ("basic_instance.inst.cfg", {"metaData": {"name": "Basic"}}),
    ("metadata_instance.inst.cfg", {"metaData": {"name": "Metadata", "author": "Ultimaker", "bool": "False", "integer": "6"}}),
    ("setting_values.inst.cfg", {"metaData": {"name": "Setting Values"}, "values": {"test_setting_0": 20, "test_setting_1": 20,"test_setting_2": 20, "test_setting_3": 20, "test_setting_4": 20}}),
]


@pytest.mark.parametrize("filename,expected", test_deserialize_data)
def test_deserialize(filename, expected):
    instance_container = UM.Settings.InstanceContainer.InstanceContainer(filename)

    path = Resources.getPath(Resources.InstanceContainers, filename)
    with open(path, encoding = "utf-8") as data:
        instance_container.deserialize(data.read())

    for key, value in expected.items():
        if key == "values":
            for key, value in value.items():
                assert instance_container.getProperty(key, "value") == value
                # We also expect to find an single instance for every key we expect to have a value for.
                assert instance_container.getInstance(key) is not None
                assert instance_container.hasProperty(key, "value")

            all_keys = instance_container.getAllKeys()
            all_expected_keys = set(expected["values"].keys())
            assert all_keys == all_expected_keys
        elif key == "metaData":
            assert instance_container.metaData.items() >= value.items()
        else:
            assert getattr(instance_container, key) == value

    assert len(expected.get("values", [])) == len(instance_container.findInstances())

    # Check if deepcopy works
    container_copied = copy.deepcopy(instance_container)
    assert instance_container == container_copied

    # Check if clearing the container works.
    instance_container.clear()
    assert instance_container.getNumInstances() == 0


def test_serialize_withoutDefinition():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("beep")
    assert instance_container.serialize() == ""


def test__readAndValidateSerialisedWithInvalidData():
    with pytest.raises(UM.Settings.InstanceContainer.InvalidInstanceError):
        UM.Settings.InstanceContainer.InstanceContainer._readAndValidateSerialized("")

def test_deserializeWithInvalidData():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("")

    # Version is not an integer
    with pytest.raises(UM.Settings.InstanceContainer.IncorrectInstanceVersionError):
        instance_container.deserialize("[general]\ndefinition = nope\nversion=Turtles")

    # Version is not the correct one (but does have the correct format
    with pytest.raises(UM.Settings.InstanceContainer.IncorrectInstanceVersionError):
        instance_container.deserialize("[general]\ndefinition = nope\nversion=9001")


def test_deserializeMetadataInvalid():
    with pytest.raises(UM.Settings.InstanceContainer.InvalidInstanceError):
        UM.Settings.InstanceContainer.InstanceContainer.deserializeMetadata("", "whatever")


@pytest.mark.parametrize("filename,expected", test_deserialize_data)
def test_deserialiseMetadata(filename, expected):
    instance_container = UM.Settings.InstanceContainer.InstanceContainer(filename)

    path = Resources.getPath(Resources.InstanceContainers, filename)
    with open(path, encoding="utf-8") as data:
        metadata = instance_container.deserializeMetadata(data.read(), filename)

    # We're only interested in the metadata now.
    for key, value in expected["metaData"].items():
        assert metadata[0][key] == value


@pytest.mark.parametrize("filename,expected", test_deserialize_data)
def test_duplicate(filename, expected):
    instance_container = UM.Settings.InstanceContainer.InstanceContainer(filename)

    path = Resources.getPath(Resources.InstanceContainers, filename)
    with open(path, encoding="utf-8") as data:
        instance_container.deserialize(data.read())

    duplicated_container = instance_container.duplicate(instance_container.getId())
    assert duplicated_container == instance_container


def test_compare():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("setting_values.inst.cfg")
    path = Resources.getPath(Resources.InstanceContainers, "setting_values.inst.cfg")
    with open(path, encoding="utf-8") as data:
        instance_container.deserialize(data.read())

    # Time to do some checking!
    assert not instance_container == instance_container.duplicate("different_id")
    assert instance_container != instance_container.duplicate("different_id")

    container_with_added_metadata = instance_container.duplicate(instance_container.getId())
    container_with_added_metadata.setMetaDataEntry("yay", "whoo")
    assert not instance_container == container_with_added_metadata

    container_with_changed_metadata = instance_container.duplicate(instance_container.getId())
    container_with_changed_metadata.setMetaData({"name": "SomethingDifferentAlltogether!"})
    assert not instance_container == container_with_changed_metadata

    container_with_removed_instance = instance_container.duplicate(instance_container.getId())
    container_with_removed_instance.removeInstance("test_setting_0")
    assert not instance_container == container_with_removed_instance


def test_setMetadata():
    container = UM.Settings.InstanceContainer.InstanceContainer("test")
    container.metaDataChanged = unittest.mock.MagicMock()
    container.setMetaDataEntry("YAY", "whoo")
    assert container.metaDataChanged.emit.call_count == 1
    assert container.getMetaDataEntry("YAY") == "whoo"

    # Setting it again shouldn't trigger a notification
    container.setMetaDataEntry("YAY", "whoo")
    assert container.metaDataChanged.emit.call_count == 1

    # Actually changing it should trigger an update.
    container.setMetaDataEntry("YAY", "woot")
    assert container.metaDataChanged.emit.call_count == 2
    assert container.getMetaDataEntry("YAY") == "woot"

    # Setting the entire metadata to the same value should also not trigger an update.
    container.setMetaData(container.getMetaData())
    assert container.metaDataChanged.emit.call_count == 2


def test_getSetPath():
    container = UM.Settings.InstanceContainer.InstanceContainer("test")
    container.setPath("WHATEVERRRR")
    assert container.getPath() == "WHATEVERRRR"


def test_addInstance():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")

    definition1 = UM.Settings.SettingDefinition.SettingDefinition("test_0", None)
    definition1.deserialize({
        "label": "Test 0",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0,
        "minimum_value": "test_1 / 10",
    })
    def1_instance = UM.Settings.SettingInstance.SettingInstance(definition1, instance_container)
    def1_instance.propertyChanged = unittest.mock.MagicMock()

    instance_container.addInstance(def1_instance)
    assert def1_instance.propertyChanged.emit.call_count == 1
    assert instance_container.getInstance("test_0") == def1_instance

    # Adding it again shouldn't have an impact.
    instance_container.addInstance(def1_instance)
    assert def1_instance.propertyChanged.emit.call_count == 1


def test_getUnknownInstance():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")
    assert instance_container.getInstance("HERP DERP") is None


def test_lt_compare():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")
    instance_container.setMetaDataEntry("weight", 12)

    instance_container2 = UM.Settings.InstanceContainer.InstanceContainer("test2")
    instance_container2.setMetaDataEntry("weight", 2)

    assert instance_container2 < instance_container

    assert instance_container2 < None

    instance_container2.setMetaDataEntry("weight", 0)
    instance_container.setMetaDataEntry("weight", 0)
    instance_container2.setName("b")
    instance_container.setName("a")
    assert instance_container < instance_container2


def test_dirty_instance_container():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")
    assert not instance_container.isDirty()
    instance_container.setDirty(True)
    assert instance_container.isDirty()

    # Make the instance container think it's read only.
    instance_container._read_only = True
    instance_container.setDirty(False)
    assert instance_container.isDirty()  # Changing it is no longer possible


def test_getAllKeys():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")
    definition1 = UM.Settings.SettingDefinition.SettingDefinition("test_0", None)
    definition1.deserialize({
        "label": "Test 0",
        "type": "float",
        "description": "A Test Setting",
        "default_value": 10.0
    })
    def1_instance = UM.Settings.SettingInstance.SettingInstance(definition1, instance_container)
    def1_instance.propertyChanged = unittest.mock.MagicMock()

    instance_container.addInstance(def1_instance)


def test_getAllKeys_cached():
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")
    instance_container.setCachedValues({"beep": "yay"})

    assert instance_container.getAllKeys() == {"beep"}


def test_hasPropertyValueCached():
    # We special cased the value property if it's in the cache.
    instance_container = UM.Settings.InstanceContainer.InstanceContainer("test")
    instance_container.setCachedValues({"beep": "yay"})
    assert instance_container.hasProperty("beep", "value")