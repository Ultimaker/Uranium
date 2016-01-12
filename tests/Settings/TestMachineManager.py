import pytest

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