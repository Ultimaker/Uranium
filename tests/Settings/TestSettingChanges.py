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
        if setting_name not in self._profile_change_count:
            return 0

        return self._profile_change_count[setting_name]

    def getTotalProfileChangeCount(self):
        count = 0
        for key in self._profile_change_count:
            count += self._profile_change_count[key]

        return count

    def _onSettingValueChanged(self, setting_name):
        if setting_name not in self._profile_change_count:
            self._profile_change_count[setting_name] = 0

        self._profile_change_count[setting_name] += 1

    def clear(self):
        self._profile_change_count = { }

class TestSettingChanges():
    def test_simple_change(self, application, machine_manager):
        definition, profile = self._createProfile(machine_manager, "setting_change_simple.json")

        assert definition.getId() == "test_setting_change_simple"

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

        listener.clear()

        profile.setSettingValue("test_setting_0_child_0", 20)
        profile.setSettingValue("test_setting_0", 60)

        assert listener.getProfileChangeCount("test_setting_0") == 1
        assert listener.getProfileChangeCount("test_setting_0_child_0") == 1
        assert listener.getProfileChangeCount("test_setting_0_child_1") == 1

        assert len(profile.getChangedSettings()) == 2

        assert profile.getSettingValue("test_setting_0") == 60
        assert profile.getSettingValue("test_setting_0_child_0") == 20
        assert profile.getSettingValue("test_setting_0_child_1") == 300

    test_change_noparent_data = [
        ({ "test_setting_0": 20 }, {
             "changed_setting_count": 1,
             "total_change_signals": 2,
             "test_setting_0": { "change_signals": 1, "value": 20 },
             "test_setting_1": { "change_signals": 1, "value": 40 },
             "test_setting_2": { "change_signals": 0, "value": 15 },
             "test_setting_3": { "change_signals": 0, "value": 5 }
        }),
        ({ "test_setting_3": 10 }, {
             "changed_setting_count": 1,
             "total_change_signals": 2,
             "test_setting_0": { "change_signals": 0, "value": 10 },
             "test_setting_1": { "change_signals": 0, "value": 20 },
             "test_setting_2": { "change_signals": 1, "value": 30 },
             "test_setting_3": { "change_signals": 1, "value": 10 }
        }),
        ({ "test_setting_0": 20, "test_setting_3": 10 }, {
             "changed_setting_count": 2,
             "total_change_signals": 4,
             "test_setting_0": { "change_signals": 1, "value": 20 },
             "test_setting_1": { "change_signals": 1, "value": 40 },
             "test_setting_2": { "change_signals": 1, "value": 30 },
             "test_setting_3": { "change_signals": 1, "value": 10 }
        }),
        ({ "test_setting_1": 40, "test_setting_2": 30 }, {
             "changed_setting_count": 2,
             "total_change_signals": 2,
             "test_setting_0": { "change_signals": 0, "value": 10 },
             "test_setting_1": { "change_signals": 1, "value": 40 },
             "test_setting_2": { "change_signals": 1, "value": 30 },
             "test_setting_3": { "change_signals": 0, "value": 5 }
        }),
    ]

    @pytest.mark.parametrize("setting_changes,expected", test_change_noparent_data)
    def test_change_noparent(self, application, machine_manager, setting_changes, expected):
        definition, profile = self._createProfile(machine_manager, "setting_change_noparent.json")

        listener = SettingChangeListener(profile)

        assert definition.getId() == "test_setting_change_noparent"

        assert profile.getSettingValue("test_setting_0") == 10
        assert profile.getSettingValue("test_setting_1") == 20
        assert profile.getSettingValue("test_setting_2") == 15
        assert profile.getSettingValue("test_setting_3") == 5

        for key, value in setting_changes.items():
            profile.setSettingValue(key, value)

        assert len(profile.getChangedSettings()) == expected.pop("changed_setting_count")
        assert listener.getTotalProfileChangeCount() == expected.pop("total_change_signals")
        for key, value in expected.items():
            assert listener.getProfileChangeCount(key) == value["change_signals"]
            assert profile.getSettingValue(key) == value["value"]

    def _createProfile(self, machine_manager, definition_file):
        definition = MachineDefinition(machine_manager, os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", definition_file))
        definition.loadAll()
        machine_manager.addMachineDefinition(definition)
        instance = MachineInstance(machine_manager, definition = definition)
        machine_manager.addMachineInstance(instance)
        machine_manager.setActiveMachineInstance(instance)
        profile = Profile(machine_manager)
        machine_manager.addProfile(profile)
        machine_manager.setActiveProfile(profile)

        return (definition, profile)