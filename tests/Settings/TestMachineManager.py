import pytest
import os

from UM.Settings.MachineDefinition import MachineDefinition

class TestMachineManager():
    def test_emptyManager(self, machine_manager):
        assert machine_manager.getApplicationName() == "test"
        assert machine_manager.getMachineDefinitions() == []
        assert machine_manager.getAllMachineVariants("none") == []
        assert machine_manager.findMachineDefinition("none") is None
        assert machine_manager.getActiveMachineInstance() is None
        assert machine_manager.getProfiles() == []
        assert machine_manager.getProfileReaders() == {}.items()
        assert machine_manager.getProfileWriters() == {}.items()


    def test_addAndFindDefinition(self, machine_manager):
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath("basic.json"))
        machine_manager.addMachineDefinition(definition)

        # No data is loaded, the definition should not have a name (and thus, no machine with test_basic should be found!)
        assert machine_manager.findMachineDefinition("test_basic") == None
        definition.loadMetaData()

        # Data is now loaded, so finding the definition should be possible
        assert machine_manager.findMachineDefinition("test_basic") == definition

        assert machine_manager.getMachineDefinitions() == [definition]
        assert machine_manager.getMachineDefinitions(include_variants = False) == [definition]

    def test_variants(self, machine_manager):
        definition_1 = MachineDefinition(machine_manager, self._getDefinitionsFilePath("variant_1.json"))
        definition_1.loadMetaData()
        machine_manager.addMachineDefinition(definition_1)
        definition_2 = MachineDefinition(machine_manager, self._getDefinitionsFilePath("variant_2.json"))
        definition_2.loadMetaData()
        machine_manager.addMachineDefinition(definition_2)

        returned_definitions = machine_manager.getMachineDefinitions()
        assert definition_1 in returned_definitions and definition_2 in returned_definitions

        returned_definitions = machine_manager.getMachineDefinitions(include_variants = False)
        # Check if only one of the definitions is returned.
        assert (definition_1 in returned_definitions) != (definition_2 in returned_definitions)

        returned_definitions = machine_manager.getAllMachineVariants("variant")
        assert definition_1 in returned_definitions and definition_2 in returned_definitions

        assert machine_manager.findMachineDefinition("variant", "Variant test 1") == definition_1
        assert machine_manager.findMachineDefinition("variant", "Variant test 2") == definition_2
        assert machine_manager.findMachineDefinition("variant", "Not existing variant") is None



    def _getDefinitionsFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)