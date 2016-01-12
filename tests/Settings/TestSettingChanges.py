# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path

from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.Profile import Profile

class SettingChangeListener():
    def __init__(self, profile):
        profile.settingValueChanged.connect(self._onSettingValueChanged)

        self._profile_change_count = { }

    def getProfileChangeCount(self, setting_name):
        if not setting_name in self._profile_change_count:
            return 0

        return self._profile_change_count[setting_name]

    def _onSettingValueChanged(self, setting_name):
        if not setting_name in self._profile_change_count:
            self._profile_change_count[setting_name] = 0

        self._profile_change_count[setting_name] += 1

    def clear(self):
        self._profile_change_count = { }

class TestSettingChanges():
    def test_simple_change(self, application, machine_manager):
        definition = MachineDefinition(machine_manager, self._getFilePath("setting_change.json"))
        definition.loadAll()
        machine_manager.addMachineDefinition(definition)
        instance = MachineInstance(machine_manager, definition = definition)
        machine_manager.addMachineInstance(instance)
        machine_manager.setActiveMachineInstance(instance)
        profile = Profile(machine_manager)
        machine_manager.addProfile(profile)
        machine_manager.setActiveProfile(profile)

        assert definition.getId() == "test_setting_change"

        assert definition.isSetting("test_setting_0")
        assert definition.isSetting("test_setting_0_child_0")
        assert definition.isSetting("test_setting_0_child_1")

        listener = SettingChangeListener(profile)

        assert profile.getSettingValue("test_setting_0") == 10
        assert profile.getSettingValue("test_setting_0_child_0") == 10
        assert profile.getSettingValue("test_setting_0_child_1") == 50

        profile.setSettingValue("test_setting_0", 20)

        assert listener.getProfileChangeCount("test_setting_0") == 1
        assert listener.getProfileChangeCount("test_setting_0_child_0") == 1
        assert listener.getProfileChangeCount("test_setting_0_child_1") == 1

        assert len(profile.getChangedSettings()) == 1

        assert profile.getSettingValue("test_setting_0") == 20
        assert profile.getSettingValue("test_setting_0_child_0") == 20
        assert profile.getSettingValue("test_setting_0_child_1") == 100

        listener.clear()

        profile.setSettingValue("test_setting_0", 50)

        assert listener.getProfileChangeCount("test_setting_0") == 1
        assert listener.getProfileChangeCount("test_setting_0_child_0") == 1
        assert listener.getProfileChangeCount("test_setting_0_child_1") == 1

        assert len(profile.getChangedSettings()) == 1

        assert profile.getSettingValue("test_setting_0") == 50
        assert profile.getSettingValue("test_setting_0_child_0") == 50
        assert profile.getSettingValue("test_setting_0_child_1") == 250



    def _getFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)
