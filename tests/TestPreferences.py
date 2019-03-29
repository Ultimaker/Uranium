from unittest.mock import MagicMock
import os
from io import StringIO
from UM.Preferences import Preferences
import pytest
from UM.Resources import Resources

Resources.addSearchPath(os.path.dirname(os.path.abspath(__file__)))


test_Preference_data = [
    {"key": "test/zomg", "default": 10},
    {"key": "test/BLORP", "default": "True"},
    {"key": "testing/BLORP", "default": "False"},
    {"key": "testing/omgzomg", "default": dict()}
]

test_newValues_data = [None, 10, "omgzomg", -20, 12.1, 2j, {"test", "more_test"}, [10, 20, 30], "True", "true", dict()]


# Preferences parses "True" to True and "False" to False
def parseValue(value):
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        return value


def test_readWrite():
    preferences = Preferences()
    path = Resources.getPath(Resources.Preferences, "preferences_test.cfg")
    preferences.readFromFile(path)

    # Check if it has been loaded correctly
    assert preferences.getValue("general/foo") == "omgzomg"
    assert preferences.getValue("general/derp") == True

    # Write contents of the preference to a buffer
    in_memory_storage = StringIO()
    preferences.writeToFile(in_memory_storage)  # type: ignore

    new_preferences = Preferences()
    # For some reason, if write was used, the read doesn't work. If we do it like this, it does work.
    new_preferences.readFromFile(StringIO(in_memory_storage.getvalue()))

    assert preferences.getValue("general/foo") == new_preferences.getValue("general/foo")
    assert preferences.getValue("test/more_test") == new_preferences.getValue("test/more_test")


def test_deserialize():
    preferences = Preferences()
    path = Resources.getPath(Resources.Preferences, "preferences_test.cfg")

    with open(path, "r", encoding="utf-8") as f:
        preferences.deserialize(f.read())
    assert preferences.getValue("general/foo") == "omgzomg"
    assert preferences.getValue("general/derp") == True


def test_malformattedKey():
    preferences = Preferences()
    with pytest.raises(Exception):
        preferences.addPreference("DERP", "DERP")


@pytest.mark.parametrize("preference", test_Preference_data)
def test_addPreference(preference):
    preferences = Preferences()
    preferences.addPreference(preference["key"], preference["default"])
    assert preferences.getValue(preference["key"]) == parseValue(preference["default"])

    # Attempt to add the preference again, but with a different default.
    preferences.addPreference(preference["key"], preference["key"])
    assert preferences.getValue(preference["key"]) == parseValue(preference["key"])


@pytest.mark.parametrize("preference", test_Preference_data)
def test_removePreference(preference):
    preferences = Preferences()
    preferences.addPreference(preference["key"], preference["default"])
    preferences.removePreference(preference["key"])
    assert preferences.getValue(preference["key"]) is None


@pytest.mark.parametrize("new_value", test_newValues_data)
def test_setResetValue(new_value):
    preferences = Preferences()
    default_value = "omgzomg"
    preferences.preferenceChanged.emit = MagicMock()
    preferences.addPreference("test/test", default_value)
    assert preferences.preferenceChanged.emit.call_count == 0
    preferences.setValue("test/test", new_value)
    assert preferences.getValue("test/test") == parseValue(new_value)

    if new_value != default_value:
        assert preferences.preferenceChanged.emit.call_count == 1

    preferences.resetPreference("test/test")
    if new_value != default_value:
        assert preferences.preferenceChanged.emit.call_count == 2
    else:
        # The preference never changed. Neither the set or the reset should trigger an emit.
        assert preferences.preferenceChanged.emit.call_count == 0

    assert preferences.getValue("test/test") == default_value


def test_nonExistingSetting():
    preferences = Preferences()
    # Test that attempting to modify a non existing setting in any way doesn't break things.
    preferences.setDefault("nonExistingPreference", "whatever")
    preferences.setValue("nonExistingPreference", "whatever")
    preferences.removePreference("nonExistingPreference")