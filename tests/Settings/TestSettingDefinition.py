# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

import UM.Settings

def test_create():
    definition = UM.Settings.SettingDefinition("test", None)

    assert definition is not None
    assert definition.getKey() is "test"
    assert definition.getContainer() is None

def test_deserialize():
    definition = UM.Settings.SettingDefinition("test", None)

    definition.deseralize({})
