# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import unittest
import collections

from UM.Signal import Signal
from UM.i18n import i18nCatalog

from UM.Settings.MachineManager import MachineManager
from UM.Settings.Setting import Setting

class TestMachineManager():
    def __init__(self):
        self.activeProfileChanged = Signal()

    def getActiveProfile(self):
        return None

class TestProfile():
    def __init__(self, root_setting):
        self._root_setting = root_setting

    def getSettingValue(self, key):
        setting = self._root_setting.getSetting(key)
        if setting:
            return setting.getDefaultValue()

        return None

class TestSetting(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self._machine_manager = TestMachineManager()
        self._catalog = i18nCatalog("TestSetting")

    def tearDown(self):
        # Called after the last testfunction was executed
        self._machine_manager = None
        self._catalog = None

    def test_construct(self):
        # Most basic construction, only required arguments.
        setting = Setting(self._machine_manager, "test", self._catalog)

        # This check is mostly to see if the object was constructed properly
        self.assertIsInstance(setting, Setting)
        self.assertEqual("test", setting.getKey())

        # Construct with keyword arguments
        setting = Setting(
            self._machine_manager, "test", self._catalog,
            label = "Test Setting",
            type = "string",
        )

        self.assertIsInstance(setting, Setting)
        self.assertEqual("test", setting.getKey())
        self.assertEqual("Test Setting", setting.getLabel())
        self.assertEqual("string", setting.getType())

    def test_fillByDict(self):
        setting = Setting(self._machine_manager, "test", self._catalog)

        data = {
            "type": "int",
            "default": 4,
            "label": "Test Setting",
            "description": "A Test Setting",
            "unit": "furlongs per fortnight",
            "visible": True
        }

        setting.fillByDict(data)

        self.assertEqual("int", setting.getType())
        self.assertEqual(4, setting.getDefaultValue())
        self.assertEqual("Test Setting", setting.getLabel())
        self.assertEqual("A Test Setting", setting.getDescription())
        self.assertEqual("furlongs per fortnight", setting.getUnit())
        self.assertTrue(setting.isVisible())

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

        profile = TestProfile(setting)

        self.assertEqual(len(setting.getChildren()), 3)

        child1 = setting.getChildren()[0]
        child2 = setting.getChildren()[1]
        child3 = setting.getChildren()[2]
        # Children should keep the order in which they were defined
        self.assertEqual("test_child1", child1.getKey())
        self.assertEqual("test_child2", child2.getKey())
        self.assertEqual("test_child3", child3.getKey())

        # All children should have "setting" as their parent.
        self.assertEqual(setting, child1.getParent())
        self.assertEqual(setting, child2.getParent())
        self.assertEqual(setting, child3.getParent())

        # Child visibility should not affect parent visibility.
        self.assertTrue(setting.isVisible())

        # Child 1 uses default inheritance so should inherit its parent value
        self.assertEqual(4, child1.getDefaultValue(profile))

        # Child 2 does not inherit so should return its default value
        self.assertEqual(5, child2.getDefaultValue(profile))

        # Child 3 uses an inherit function and should return parent's value * 10.
        self.assertEqual(40, child3.getDefaultValue(profile))

    def test_parseValue(self):
        setting = Setting(self._machine_manager, "test", self._catalog, type = "int")

        self.assertEqual(setting.parseValue("1"), 1)
        self.assertEqual(setting.parseValue(1), 1)
        self.assertEqual(setting.parseValue(True), 1)
        self.assertEqual(setting.parseValue(False), 0)
        self.assertEqual(setting.parseValue(1.1), 1)

        # An error value should return a default value valid for the setting type.
        self.assertEqual(setting.parseValue("something"), 0)

        setting = Setting(self._machine_manager, "test", self._catalog, type = "boolean")

        self.assertEqual(setting.parseValue("True"), True)
        self.assertEqual(setting.parseValue(1), True)
        self.assertEqual(setting.parseValue(1.0), True)
        self.assertEqual(setting.parseValue("False"), False)
        self.assertEqual(setting.parseValue(0), False)
        self.assertEqual(setting.parseValue(-1), True)

        # Value should be a valid python literal expression
        self.assertEqual(setting.parseValue("true"), False)

        setting = Setting(self._machine_manager, "test", self._catalog, type = "float")

        self.assertEqual(setting.parseValue("1.0"), 1.0)
        self.assertEqual(setting.parseValue(1), 1.0)
        self.assertEqual(setting.parseValue(True), 1.0)

        # Floats should also be able to be specified using , as decimal separator.
        self.assertEqual(setting.parseValue("1,0"), 1.0)

        self.assertEqual(setting.parseValue("something"), 0.0)

if __name__ == "__main__":
    unittest.main()
