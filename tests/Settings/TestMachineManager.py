import pytest
import os

from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.Profile import Profile

from UM.Settings.SettingsError import DuplicateProfileError


class TestMachineManager():
    def test_emptyManager(self, machine_manager):
        assert machine_manager.getApplicationName() == "test"
        assert machine_manager.getMachineDefinitions() == []
        assert machine_manager.getAllMachineVariants("none") == []
        assert machine_manager.findMachineDefinition("none") is None
        assert machine_manager.findMachineInstance("Not there") is None
        assert machine_manager.getActiveMachineInstance() is None
        assert machine_manager.getMachineInstances() == []
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

        machine_instance = MachineInstance(machine_manager, definition = definition_1)
        machine_manager.addMachineInstance(machine_instance)
        machine_manager.setActiveMachineInstance(machine_instance)

        machine_manager.setActiveMachineVariant("Variant test 2")
        assert machine_manager.getActiveMachineInstance().getMachineDefinition() == definition_2

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

    def test_instances(self, machine_manager):
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath("basic.json"))
        definition.loadMetaData()
        machine_manager.addMachineDefinition(definition)

        machine_instance = MachineInstance(machine_manager, definition = definition, name = "Basic Test")
        machine_manager.addMachineInstance(machine_instance)
        assert machine_manager.getMachineInstances() == [machine_instance]
        assert machine_manager.findMachineInstance("Basic Test") == machine_instance
        machine_manager.setActiveMachineInstance(machine_instance)
        assert machine_manager.getActiveMachineInstance() == machine_instance

        machine_manager.removeMachineInstance(machine_instance)
        assert machine_manager.getMachineInstances() == []

    def test_profiles(self, machine_manager):
        profile_1 = Profile(machine_manager)
        profile_2 = Profile(machine_manager)
        definition = MachineDefinition(machine_manager, self._getDefinitionsFilePath("simple_machine.json"))
        definition.loadMetaData()
        machine_manager.addMachineDefinition(definition)

        machine_instance = MachineInstance(machine_manager, definition = definition, name = "Basic Test")
        machine_instance.loadFromFile(self._getInstancesFilePath("simple_machine.cfg"))
        machine_manager.addMachineInstance(machine_instance)
        profile_1._active_instance = machine_instance
        profile_2._active_instance = machine_instance

        profile_1.loadFromFile(self._getProfileFilePath("simple_machine_with_overrides.cfg"))
        profile_2.loadFromFile(self._getProfileFilePath("simple_machine_with_overrides.cfg"))
        machine_manager.addProfile(profile_1)
        assert machine_manager.getProfiles() == [profile_1]

        # Check if adding again has no effect
        machine_manager.addProfile(profile_1)
        assert machine_manager.getProfiles() == [profile_1]

        # Check that adding another profile with same name does not work
        with pytest.raises(DuplicateProfileError):
            machine_manager.addProfile(profile_2)

        # Changing the name and then adding it should work
        profile_2.setName("test")
        machine_manager.addProfile(profile_2)
        assert profile_1 in machine_manager.getProfiles() and profile_2 in machine_manager.getProfiles()

        assert machine_manager.findProfile("test") == profile_2

        # Check if removing one of the profiles works
        machine_manager.removeProfile(profile_1)
        assert machine_manager.getProfiles() == [profile_2]

        machine_manager.setActiveProfile(profile_2)
        assert machine_manager.getActiveProfile() == profile_2

        machine_manager.removeProfile(profile_2)
        
        assert machine_manager.getProfiles() == []

    def _getProfileFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles", file)

    def _getDefinitionsFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)

    def _getInstancesFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances", file)