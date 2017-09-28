# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest

import UM.Settings.SettingRelation

def test_create():
    with pytest.raises(ValueError):
        relation = UM.Settings.SettingRelation.SettingRelation(None, 2, UM.Settings.SettingRelation.RelationType.RequiresTarget, "max")

    with pytest.raises(ValueError):
        relation = UM.Settings.SettingRelation.SettingRelation(1, None, UM.Settings.SettingRelation.RelationType.RequiresTarget, "max")

    relation = UM.Settings.SettingRelation.SettingRelation(1, 2, UM.Settings.SettingRelation.RelationType.RequiresTarget, "max")
    assert relation.owner == 1
    assert relation.target == 2
    assert relation.type == UM.Settings.SettingRelation.RelationType.RequiresTarget
    assert relation.role == "max"

    relation = UM.Settings.SettingRelation.SettingRelation(1, 2, UM.Settings.SettingRelation.RelationType.RequiredByTarget, "min")
    assert relation.owner == 1
    assert relation.target == 2
    assert relation.type == UM.Settings.SettingRelation.RelationType.RequiredByTarget
    assert relation.role == "min"