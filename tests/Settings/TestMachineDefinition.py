# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path

from UM.Settings.MachineManager import MachineManager
from UM.Settings.MachineDefinition import MachineDefinition

class TestMachineDefinition():
    test_loadMetaData_data = [
        ("basic.json", {
            "id": "test_basic",
            "name": "Basic Test",
            "visible": True,
            "variant_name": "",
            "manufacturer": "Unknown Manufacturer",
            "author": "Unknown Author"
        }),
        ("all_metadata.json", {
            "id": "test_all_metadata",
            "name": "All Metadata Test",
            "visible": False,
            "variant_name": "Test Variant",
            "manufacturer": "Test Manufacturer",
            "author": "Test Author"
        }),
        ("inheritance_child.json", {
            "id": "test_inheritance_child",
            "name": "Inheritance Test (Child)",
            "visible": True,
            "variant_name": "",
            "manufacturer": "Unknown Manufacturer",
            "author": "Unknown Author"
        }),
    ]

    @pytest.mark.parametrize("file_name, expected", test_loadMetaData_data)
    def test_loadMetaData(self, machine_manager, file_name, expected):
        definition = MachineDefinition(machine_manager, self._getFilePath(file_name))

        definition.loadMetaData()

        assert definition.getId() == expected["id"]
        assert definition.getName() == expected["name"]
        assert definition.isVisible() == expected["visible"]
        assert definition.getVariantName() == expected["variant_name"]
        assert definition.getManufacturer() == expected["manufacturer"]
        assert definition.getAuthor() == expected["author"]

    def test_loadAll(self):
        pass

    def _getFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)


if __name__ == "__main__":
    unittest.main()
