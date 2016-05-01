# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import UM.Settings

def test_instance_container():
    container = UM.Settings.InstanceContainer()

def test_advanced_setProperty(instance_container):
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

