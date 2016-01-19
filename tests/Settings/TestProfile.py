# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os
import configparser

from UM.Settings.Profile import Profile

from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineManager import MachineManager

class TestProfile():

    def test_createProfile(self, machine_manager):
        profile = Profile(machine_manager)
        assert isinstance(profile, Profile)

        profile = Profile(machine_manager, read_only = True)
        assert isinstance(profile, Profile)
        assert profile.isReadOnly()

    test_profileOverride_data = [("machine_settings.json", "machine_settings.cfg", "machine_settings.cfg", {
                                                                                        "test_setting_0": 0,
                                                                                        "test_setting_1": 1,
                                                                                        "test_setting_2": True,
                                                                                        "test_setting_3": "3",
                                                                                        "test_setting_4": [ 4, 4 ]
                                                                                    }),
                                  ("machine_settings.json", "machine_settings_with_overrides.cfg", "machine_settings.cfg", {
                                                                                        "test_setting_0": "1",
                                                                                        "test_setting_1": "0",
                                                                                        "test_setting_2": "false",
                                                                                        "test_setting_3": '"4"',
                                                                                        "test_setting_4": "true"
                                                                                    }),
                                  ("machine_settings.json", "machine_settings_with_overrides.cfg", "machine_settings_with_overrides.cfg", {
                                                                                        "test_setting_0": "1"
                                                                                    }),
                                  ("simple_machine.json", "simple_machine_with_overrides.cfg", "simple_machine_with_overrides.cfg", {
                                                                                        "test_setting_0": '"overriden"',
                                                                                        "test_setting_5": 1.0,
                                                                                        "test_setting_6": 0.5,
                                                                                        "test_setting_7": False
                                                                                    })
                                  ]
    @pytest.mark.parametrize("definition_file_name, instance_file_name, profile_file_name, expected_values", test_profileOverride_data)
    def test_profileOverride(self, machine_manager, definition_file_name, instance_file_name, profile_file_name, expected_values):
        profile = Profile(machine_manager)
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath(definition_file_name))
        definition.loadMetaData()

        machine_manager.addMachineDefinition(definition)

        machine_instance = MachineInstance(machine_manager, definition = definition)
        machine_instance.loadFromFile(self._getInstancesFilePath(instance_file_name))
        profile._active_instance = machine_instance
        profile.loadFromFile(self._getProfileFilePath(profile_file_name))

        for key in expected_values:
            assert profile.getSettingValue(key) == expected_values[key]

    test_loadAndSave_data = [("simple_machine.json", "simple_machine_with_overrides.cfg", "simple_machine_with_overrides.cfg", "simple_machine_with_overrides_test.cfg")]
    @pytest.mark.parametrize("definition_file_name, instance_file_name, profile_file_name, target_profile_file_name", test_loadAndSave_data)
    def test_loadAndSave(self, machine_manager, definition_file_name, instance_file_name, profile_file_name, target_profile_file_name):
        profile = Profile(machine_manager)
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath(definition_file_name))
        definition.loadMetaData()

        machine_manager.addMachineDefinition(definition)

        machine_instance = MachineInstance(machine_manager, definition = definition)
        machine_instance.loadFromFile(self._getInstancesFilePath(instance_file_name))
        profile._active_instance = machine_instance
        profile.loadFromFile(self._getProfileFilePath(profile_file_name))
        try:
            os.remove(self._getProfileFilePath(target_profile_file_name)) # Clear any previous tests
        except:
            pass
        profile.saveToFile(self._getProfileFilePath(target_profile_file_name))

        config_loaded = configparser.ConfigParser()
        config_loaded.read(self._getProfileFilePath(instance_file_name))
        config_saved = configparser.ConfigParser()
        config_saved.read(self._getProfileFilePath(target_profile_file_name))

        for section in config_loaded.sections():
            assert section in config_saved.sections()
            for key in config_loaded[section]:
                assert key in config_saved[section]
                assert config_loaded[section][key] == config_saved[section][key]


    def _getProfileFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles", file)

    def _getDefinitionsFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)

    def _getInstancesFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances", file)