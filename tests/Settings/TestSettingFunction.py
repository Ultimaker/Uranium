# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

import UM.Settings.SettingFunction

##  Individual test cases for the good setting functions.
#
#   Each test will be executed with each of these functions. These functions are
#   all good and should work.
setting_function_good_data = [
    "0",            # Number.
    "\"x\"",        # String.
    "True",         # Boolean.
    "foo",          # Variable.
    "math.sqrt(4)", # Function call.
    "foo * zoo"     # Two variables.
]

##  Fixture to create a setting function.
#
#   These setting functions are all built with good functions. Id est no errors
#   should occur during the creation of the fixture.
@pytest.fixture(params = setting_function_good_data)
def setting_function_good(request):
    return UM.Settings.SettingFunction.SettingFunction(request.param)

##  Individual test cases for the bad setting functions.
#
#   Each test will be executed with each of these functions. These functions are
#   all bad and should not work.
setting_function_bad_data = [
    "",                                                                 # Empty string.
    "os.read(os.open(\"/etc/passwd\", os.O_RDONLY), 10)",               # Function that reads your passwords from your system.
    "exec(\"os.read(os.open(\\\"/etc/passwd\\\", os.O_RDONLY), 10)\")", # Obfuscated function that reads your passwords from your system.
    "("                                                                 # Syntax error.
]

##  Fixture to create a setting function.
#
#   These setting functions are all built with bad functions. Id est they should
#   give an error when creating the fixture.
@pytest.fixture(params = setting_function_bad_data)
def setting_function_bad(request):
    return UM.Settings.SettingFunction.SettingFunction(request.param)

##  Tests the initialisation of setting functions with good functions.
#
#   Each of these should create a good function.
def test_init_good(setting_function_good):
    assert setting_function_good is not None
    assert setting_function_good.isValid()

##  Tests the initialisation of setting functions with bad functions.
#
#   Each of these should create a bad function.
def test_init_bad(setting_function_bad):
    assert setting_function_bad is not None
    assert not setting_function_bad.isValid()

class MockValueProvider:
    ##  Creates a mock value provider.
    #
    #   This initialises a dictionary with key-value pairs.
    def __init__(self):
        self._values = {
            "foo": 5,
            "zoo": 7
        }

    ##  Provides a value.
    #
    #   \param name The key of the value to provide.
    def getValue(self, name):
        if not (name in self._values):
            return None
        return self._values[name]

test_call_data = [
    { "code": "0",            "result": 0 },
    { "code": "\"x\"",        "result": "x" },
    { "code": "True",         "result": True },
    { "code": "foo",          "result": 8 },
    { "code": "math.sqrt(4)", "result": 2 },
    { "code": "foo * zoo",    "result": 35 }, # 5 * 7
    { "code": "",             "result": None },
    { "code": "os.read(os.open(\"/etc/passwd\", os.O_RDONLY), 10)", "result": None },
    { "code": "exec(\"os.read(os.open(\\\"/etc/passwd\\\", os.O_RDONLY), 10)\")", "result": None },
    { "code": "boo",          "result": None } # Variable doesn't exist.
]

##  Tests the calling of a valid setting function.
#
#   \param setting_function_good A valid setting function from a fixture.
@pytest.mark.parametrize("data", test_call_data)
def test_call(data):
    value_provider = MockValueProvider()
    function = UM.Settings.SettingFunction.SettingFunction(data["code"])
    assert function(value_provider) == data["result"]