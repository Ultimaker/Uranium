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
    "foo",          # Variable.
    "math.sqrt(4)", # Function call.
    "foo * zoo"     # Two variables.
    "boo"           # Variable that's not provided by the value provider.
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
    "",                                                       # Empty string.
    "lambda i: os.open(/etc/passwd).read()",                  # Function that reads your passwords from your system.
    "exec(\"lambda i: o\" + \"s.open(/etc/passwd).read()\")", # Obfuscated function that reads your passwords from your system.
    "("                                                       # Syntax error.
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