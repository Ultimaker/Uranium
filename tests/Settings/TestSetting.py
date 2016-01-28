# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import collections

from UM.Signal import Signal
from UM.i18n import i18nCatalog

from UM.Settings.MachineManager import MachineManager
from UM.Settings.Setting import Setting

class MachineManager():
    def __init__(self):
        self.activeProfileChanged = Signal()

    def getActiveProfile(self):
        return None

class Profile():
    def __init__(self, root_setting):
        self._root_setting = root_setting

    def getSettingValue(self, key):
        setting = self._root_setting.getSetting(key)
        if setting:
            return setting.getDefaultValue()

        return None

class TestSetting():
    def setup_method(self, method):
        # Called before the first testfunction is executed
        self._machine_manager = MachineManager()
        self._catalog = i18nCatalog("TestSetting")

    def teardown_method(self, method):
        # Called after the last testfunction was executed
        self._machine_manager = None
        self._catalog = None

    def test_construct(self):
        # Most basic construction, only required arguments.
        setting = Setting(self._machine_manager, "test", self._catalog)

        # This check is mostly to see if the object was constructed properly
        assert isinstance(setting, Setting)
        assert setting.getKey() == "test"

        # Construct with keyword arguments
        setting = Setting(
            self._machine_manager, "test", self._catalog,
            label = "Test Setting",
            type = "string",
        )

        assert isinstance(setting, Setting)
        assert setting.getKey() == "test"
        assert setting.getLabel() == "Test Setting"
        assert setting.getType() == "string"

    test_fillByDict_data = [
        ({ "type": "boolean", "default": True, "label": "Test Boolean", "description": "A boolean test setting" }),
        ({ "type": "int", "default": 10, "label": "Test Integer", "description": "An integer test setting" }),
        ({ "type": "float", "default": True, "label": "Test Float", "description": "A float test setting" }),
        ({ "type": "string", "default": "test", "label": "Test String", "description": "A string test setting" }),
        ({ "type": "enum", "default": "one", "label": "Test Enum", "description": "An enum test setting" }),
    ]

    @pytest.mark.parametrize("data", test_fillByDict_data)
    def test_fillByDict(self, data):
        setting = Setting(self._machine_manager, "test", self._catalog)

        setting.fillByDict(data)

        assert setting.getType() == data["type"]
        assert setting.getDefaultValue() == data["default"]
        assert setting.getLabel() == data["label"]
        assert setting.getDescription() == data["description"]
        assert setting.isVisible()

    def test_fillByDictWithChildren(self):
        setting = Setting(self._machine_manager, "test", self._catalog)

        data = {
            "type": "int",
            "default": 4,
            "label": "Test Setting",
            "description": "A Test Setting",
            "unit": "furlongs per fortnight",
            "visible": True,

            # Since python's dict is unordered but we want an ordered dict we
            # have to go through a bit of magic to make sure we define it as an
            # ordered dict.
            "children": collections.OrderedDict(sorted({
                "test_child1": {
                    "type": "int",
                    "default": 9,
                    "label": "Test Child 1",
                    "description": "Test Setting Child 1",
                },
                "test_child2": {
                    "type": "int",
                    "default": 5,
                    "label": "Test Child 2",
                    "description": "Test Setting Child 2",
                    "inherit": False
                },
                "test_child3": {
                    "type": "int",
                    "default": 99,
                    "label": "Test Child 3",
                    "description": "Test Setting Child 3",
                    "inherit_function": "parent_value * 10"
                }
            }.items(), key = lambda k: k[0]))
        }

        setting.fillByDict(data)

        profile = Profile(setting)

        assert len(setting.getChildren()) == 3

        child1 = setting.getChildren()[0]
        child2 = setting.getChildren()[1]
        child3 = setting.getChildren()[2]

        # Children should keep the order in which they were defined
        assert child1.getKey() == "test_child1"
        assert child2.getKey() == "test_child2"
        assert child3.getKey() == "test_child3"

        # All children should have "setting" as their parent.
        assert child1.getParent() == setting
        assert child2.getParent() == setting
        assert child3.getParent() == setting

        # Child visibility should not affect parent visibility.
        assert setting.isVisible()

        # Child 1 uses default inheritance so should inherit its parent value
        assert child1.getDefaultValue(profile) == 4

        # Child 2 does not inherit so should return its default value
        assert child2.getDefaultValue(profile) == 5

        # Child 3 uses an inherit function and should return parent's value * 10.
        assert child3.getDefaultValue(profile) == 40

    test_parseValue_data = [
        ("int", "1", 1),
        ("int", 1, 1),
        ("int", True, 1),
        ("int", False, 0),
        ("int", 1.1, 1),
        ("int", "something", 0),
        ("boolean", "True", True),
        ("boolean", 1, True),
        ("boolean", 1.0, True),
        ("boolean", "False", False),
        ("boolean", 0, False),
        ("boolean", -1, True),
        ("boolean", "true", False),
        ("boolean", "something", False),
        ("float", "1.0", 1.0),
        ("float", "1", 1.0),
        ("float", "True", 1.0),
        ("float", "10.0", 10.0),
        ("float", "1,0", 1.0),
        ("float", "something", 0.0),
    ]

    @pytest.mark.parametrize("setting_type,data,result", test_parseValue_data)
    def test_parseValue(self, setting_type, data, result):
        setting = Setting(self._machine_manager, "test", self._catalog, type = setting_type)

        assert setting.parseValue(data) == result
