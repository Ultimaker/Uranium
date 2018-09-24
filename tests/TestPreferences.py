from unittest.mock import MagicMock

from UM.Preferences import Preferences
import pytest

test_Preference_data = [
    {"key": "zomg", "default": 10},
    {"key": "BLORP", "default": "True"},
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


@pytest.mark.parametrize("preference", test_Preference_data)
def test_addPreference(preference):
    preferences = Preferences()
    preferences.addPreference(preference["key"], preference["default"])
    assert preferences.getValue(preference["key"]) == parseValue(preference["default"])


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
    preferences.addPreference("test", default_value)
    assert preferences.preferenceChanged.emit.call_count == 0
    preferences.setValue("test", new_value)
    assert preferences.getValue("test") == parseValue(new_value)

    if new_value != default_value:
        assert preferences.preferenceChanged.emit.call_count == 1

    preferences.resetPreference("test")
    if new_value != default_value:
        assert preferences.preferenceChanged.emit.call_count == 2
    else:
        # The preference never changed. Neither the set or the reset should trigger an emit.
        assert preferences.preferenceChanged.emit.call_count == 0

    assert preferences.getValue("test") == default_value
