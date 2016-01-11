# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os
import configparser

from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineManager import MachineManager

from UM.Settings import SettingsError

class TestMachineInstance():
    test_construct_data = [("basic.json", "basic"),
                           ("machine_settings.json", "machine_settings"),
                           ("categories.json", "categories"),
                           ("inheritance_child.json", "inheritance_child")]

    @pytest.mark.parametrize("file_name, instance_name", test_construct_data)
    def test_construct(self, machine_manager, file_name, instance_name):
        # Create a definition
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath(file_name))
        definition.loadMetaData()

        machine_instance = MachineInstance(machine_manager, definition = definition, name = instance_name)
        assert isinstance(machine_instance, MachineInstance)
        assert machine_instance.getMachineDefinition() == definition
        assert machine_instance.getName() == instance_name

    test_instanceOverride_data = [("basic.json", "basic.cfg", {}),
                                  ("machine_settings.json", "machine_settings.cfg", {
                                                                                        "test_setting_0": 0,
                                                                                        "test_setting_1": 1,
                                                                                        "test_setting_2": True,
                                                                                        "test_setting_3": "3",
                                                                                        "test_setting_4": [ 4, 4 ]
                                                                                    }),
                                  ("machine_settings.json", "machine_settings_with_overrides.cfg", {
                                                                                        "test_setting_0": "1",
                                                                                        "test_setting_1": "0",
                                                                                        "test_setting_2": "false",
                                                                                        "test_setting_3": '"4"',
                                                                                        "test_setting_4": "true"
                                                                                    })]
    ## TODO: Note that in these tests the type is not taken into account, as technically machineSettings don't have
    #  a type to which it can be forcefully cast.
    @pytest.mark.parametrize("definition_file_name, instance_file_name, expected_values", test_instanceOverride_data)
    def test_instanceOverride(self, machine_manager, definition_file_name, instance_file_name, expected_values):
        # Create a definition
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath(definition_file_name))
        definition.loadMetaData()

        machine_manager.addMachineDefinition(definition)

        machine_instance = MachineInstance(machine_manager, definition = definition)
        machine_instance.loadFromFile(self._getInstancesFilePath(instance_file_name))

        for key in expected_values:
            assert machine_instance.getSettingValue(key) == expected_values[key]

    test_loadFromFileExceptions_data = [("basic.json", "invalid_file.cfg", SettingsError.InvalidFileError),
                                        ("basic.json", "unknown_type.cfg", SettingsError.DefinitionNotFoundError),
                                        ("basic.json", "invalid_version.cfg", SettingsError.SettingsError)]

    @pytest.mark.parametrize("definition_file_name, instance_file_name, expected_exception", test_loadFromFileExceptions_data)
    def test_loadFromFileExceptions(self, machine_manager, definition_file_name, instance_file_name, expected_exception):
        # Create a definition
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath(definition_file_name))
        definition.loadMetaData()

        machine_instance = MachineInstance(machine_manager, definition = definition)
        with pytest.raises(expected_exception):
            machine_instance.loadFromFile(self._getInstancesFilePath(instance_file_name))

    test_loadAndSave_data = [("machine_settings.json", "machine_settings_with_overrides.cfg", "machine_settings_with_overrides_test.cfg")]
    @pytest.mark.parametrize("definition_file_name, instance_file_name, target_instance_file_name", test_loadAndSave_data)
    def test_loadAndSave(self, machine_manager, definition_file_name, instance_file_name, target_instance_file_name):
        # Create a definition
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath(definition_file_name))
        definition.loadMetaData()

        machine_manager.addMachineDefinition(definition)

        machine_instance = MachineInstance(machine_manager, definition = definition)
        machine_instance.loadFromFile(self._getInstancesFilePath(instance_file_name))
        try:
            os.remove(self._getInstancesFilePath(target_instance_file_name)) # Clear any previous tests
        except:
            pass
        machine_instance.saveToFile(self._getInstancesFilePath(target_instance_file_name))

        config_loaded = configparser.ConfigParser()
        config_loaded.read(self._getInstancesFilePath(instance_file_name))
        config_saved = configparser.ConfigParser()
        config_saved.read(self._getInstancesFilePath(target_instance_file_name))

        for section in config_loaded.sections():
            assert section in config_saved.sections()
            for key in config_loaded[section]:
                assert key in config_saved[section]
                assert config_loaded[section][key] == config_saved[section][key]


    def _getDefinitionsFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)

    def _getInstancesFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances", file)

if __name__ == "__main__":
    unittest.main()
