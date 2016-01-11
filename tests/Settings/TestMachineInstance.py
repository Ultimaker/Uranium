# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os

from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineManager import MachineManager

from UM.Settings import SettingsError

class TestMachineInstance():
    def setup_method(self, method):
        #self._machine_manager = MachineManager()
        #self._catalog = i18nCatalog("TestSetting")
        pass

    def teardown_method(self, method):
        #self._machine_manager = None
        #self._catalog = None
        pass

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

    '''test_loadFromFile_data = [("basic.json", "basic.cfg")]
    @pytest.mark.parametrize("definition_file_name, instance_file_name", test_loadFromFile_data)
    def test_loadFromFile(self, machine_manager, definition_file_name, instance_file_name):
        # Create a definition
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath(definition_file_name))
        definition.loadMetaData()

        machine_instance = MachineInstance(machine_manager, definition = definition)
        print(machine_manager._machine_definitions)
        #with pytest.raises(InvalidFileError):
        machine_instance.loadFromFile(self._getInstancesFilePath(instance_file_name))'''

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

    def _getDefinitionsFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)

    def _getInstancesFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances", file)

if __name__ == "__main__":
    unittest.main()
