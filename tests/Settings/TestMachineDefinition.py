# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path

from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings import SettingsError

class TestMachineDefinition():
    test_loadMetaData_data = [
        # Basic test of metadata, with only the bare minimum set.
        # Should result in mostly default-initialized values.
        ("basic.json", {
            "id": "test_basic",
            "name": "Basic Test",
            "visible": True,
            "variant_name": "",
            "manufacturer": "Unknown Manufacturer",
            "author": "Unknown Author"
        }),
        # Test all possible metadata.
        ("all_metadata.json", {
            "id": "test_all_metadata",
            "name": "All Metadata Test",
            "visible": False,
            "variant_name": "Test Variant",
            "manufacturer": "Test Manufacturer",
            "author": "Test Author"
        }),
        # Metadata should not be inherited at the moment.
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

    test_loadAll_data = [
        # The most basic valid definition. Should result in an empty definition.
        ("basic.json", {
            "id": "test_basic",
            "machine_setting_count": 0,
            "category_count": 0,
        }),
        # Test that machine settings are being parsed and instantiated correctly.
        ("machine_settings.json", {
            "id": "test_machine_settings",
            "machine_setting_count": 5,
            "category_count": 0,

            "machine_settings": [
                { "id": "test_setting_0", "default": 0 },
                { "id": "test_setting_1", "default": 1.0 },
                { "id": "test_setting_2", "default": True },
                { "id": "test_setting_3", "default": "3" },
                { "id": "test_setting_4", "default": [ 4, 4 ] },
            ],
        }),
        # Test that categories, including settings, are parsed and instantiated correctly.
        ("categories.json", {
            "id": "test_categories",
            "machine_setting_count": 0,
            "category_count": 3,

            "categories": [
                {
                    "id": "test_category_0",
                    "label": "Test Category 0",
                    "visible": True,
                    "setting_count": 2,
                    "settings": [
                        { "id": "test_category_0_setting_0", "label": "Test Category 0 Test Setting 0", "type": "int", "default": 0, "visible": True },
                        { "id": "test_category_0_setting_1", "label": "Test Category 0 Test Setting 1", "type": "int", "default": 1, "visible": True },
                    ],
                },
                {
                    "id": "test_category_1",
                    "label": "Test Category 1",
                    "visible": False,
                    "setting_count": 1,
                    "settings": [
                        { "id": "test_category_1_setting_0", "label": "Test Category 1 Test Setting 0", "type": "int", "default": 0, "visible": True },
                    ],
                },
                {
                    "id": "test_category_2",
                    "label": "Test Category 2",
                    "visible": False,
                    "setting_count": 2,
                    "settings": [
                        { "id": "test_category_2_setting_0", "label": "Test Category 2 Test Setting 0", "type": "int", "default": 0, "visible": False },
                        { "id": "test_category_2_setting_1", "label": "Test Category 2 Test Setting 1", "type": "int", "default": 1, "visible": False },
                    ],
                },
            ],
        }),
        # Test that inheritance works properly.
        ("inheritance_child.json", {
            "id": "test_inheritance_child",
            "machine_setting_count": 4,
            "category_count": 4,

            "machine_settings": [
                { "id": "parent_machine_setting_0", "default": 0 },
                { "id": "parent_machine_setting_1", "default": 1 },
                { "id": "child_machine_setting_0", "default": 0 },
                { "id": "child_machine_setting_1", "default": 1 },
            ],
        }),
        # Test that overrides work properly for inheritance.
        ("inheritance_overrides.json", {
            "id": "test_inheritance_overrides",
            "machine_setting_count": 2,
            "category_count": 2,

            "machine_settings": [
                { "id": "parent_machine_setting_0", "default": 2 },
                { "id": "parent_machine_setting_1", "default": 3 },
            ],
        }),
    ]

    @pytest.mark.parametrize("file_name, expected", test_loadAll_data)
    def test_loadAll(self, machine_manager, file_name, expected):
        definition = MachineDefinition(machine_manager, self._getFilePath(file_name))
        definition.loadAll()

        assert definition.getId() == expected["id"]
        assert len(definition.getMachineSettings()) == expected["machine_setting_count"]
        assert len(definition.getAllCategories()) == expected["category_count"]

        if "machine_settings" in expected:
            for expected_setting in expected["machine_settings"]:
                assert definition.isMachineSetting(expected_setting["id"])
                assert definition.getSetting(expected_setting["id"]).getDefaultValue(None) == expected_setting["default"]

        if "categories" in expected:
            for expected_category in expected["categories"]:
                category = definition.getSettingsCategory(expected_category["id"])
                assert category is not None
                assert category.getLabel() == expected_category["label"]
                assert category.isVisible() == expected_category["visible"]
                assert len(category.getAllSettings()) == expected_category["setting_count"]

                if "settings" in expected_category:
                    for expected_setting in expected_category["settings"]:
                        setting = category.getSetting(expected_setting["id"])
                        assert setting is not None
                        assert setting.getLabel() == expected_setting["label"]
                        assert setting.isVisible() == expected_setting["visible"]
                        assert setting.getType() == expected_setting["type"]
                        assert setting.getDefaultValue(None) == expected_setting["default"]

    test_loadError_data = [
        ( "file_not_found.json", FileNotFoundError ),
        ( "error_empty.json", SettingsError.InvalidFileError ),
        ( "error_no_id.json", SettingsError.InvalidFileError ),
        ( "error_no_version.json", SettingsError.InvalidFileError ),
        ( "error_invalid_version.json", SettingsError.InvalidVersionError ),
    ]

    @pytest.mark.parametrize("file_name, exception_type", test_loadError_data)
    def test_loadError(self, machine_manager, file_name, exception_type):
        definition = MachineDefinition(machine_manager, self._getFilePath(file_name))

        with pytest.raises(exception_type):
            definition.loadAll()


    def _getFilePath(self, file):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "definitions", file)
