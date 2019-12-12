# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest
import sys

from UM.Settings.Validator import Validator, ValidatorState

##  Fake setting instance that stands in for the real setting instance.
#
#   If anything should go wrong in the real setting instance, it won't
#   influence the unit tests for the validator.
class MockSettingInstance:
    ##  Creates the mock setting instance.
    def __init__(self, value):
        self.minimum_value = None
        self.maximum_value = None
        self.minimum_value_warning = None
        self.maximum_value_warning = None
        self.warning_value = None
        self.error_value = None
        self.type = None
        self.value = value
        self.regex_blacklist_pattern = ""

    def getProperty(self, key, property_name, context = None):
        return getattr(self, property_name)

##  Called before the first test function is executed.
@pytest.fixture
def validator():
    setting_instance = MockSettingInstance(0)
    return Validator(setting_instance)

##  Tests the creation of a float validator.
#
#   \param validator A new validator from a fixture.
def test_create(validator):
    assert validator is not None

##  The individual test cases for validate().
#
#   Each entry in the list is a test.
#   Each test has:
#   - A short description for the test so we can find quickly what went
#     wrong.
#   - A minimum value for the setting.
#   - A maximum value for the setting.
#   - A current value for the setting.
#   - The answer: A state of the validator after validating the setting.
test_validate_data = [
    # Empty values
    ({"description": "Everything None",      "type": "float", "minimum": None, "maximum": None,         "min_warning": None,         "max_warning": None, "current": None,         "answer": ValidatorState.Exception}),
    # Floating point values
    ({"description": "Completely valid",     "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 5.0,          "answer": ValidatorState.Valid}),
    ({"description": "Exactly MinWarning",   "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 1.0,          "answer": ValidatorState.Valid}),
    ({"description": "Exactly MaxWarning",   "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 9.0,          "answer": ValidatorState.Valid}),
    ({"description": "Below MinWarning",     "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 0.5,          "answer": ValidatorState.MinimumWarning}),
    ({"description": "Above MaxWarning",     "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 9.5,          "answer": ValidatorState.MaximumWarning}),
    ({"description": "Exactly Minimum",      "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 0.0,          "answer": ValidatorState.MinimumWarning}),
    ({"description": "Exactly Maximum",      "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 10.0,         "answer": ValidatorState.MaximumWarning}),
    ({"description": "Below Minimum",        "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": -1.0,         "answer": ValidatorState.MinimumError}),
    ({"description": "Above Maximum",        "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 11.0,         "answer": ValidatorState.MaximumError}),
    ({"description": "Float precision test", "type": "float", "minimum": 0.0,  "maximum": 100000.0,     "min_warning": 1.0,          "max_warning": 9.0,  "current": 100000.0,     "answer": ValidatorState.MaximumWarning}),
    ({"description": "NaN value",            "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": float("nan"), "answer": ValidatorState.Exception}),
    ({"description": "NaN MinWarning",       "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": float("nan"), "max_warning": 9.0,  "current": 1.0,          "answer": ValidatorState.Valid}),
    ({"description": "Infinity Maximum",     "type": "float", "minimum": 0.0,  "maximum": float("inf"), "min_warning": 1.0,          "max_warning": 9.0,  "current": 5.0,          "answer": ValidatorState.Valid}),
    ({"description": "Maximum < MaxWarning", "type": "float", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 15.0, "current": 12.5,         "answer": ValidatorState.MaximumError}),
    ({"description": "Maximum < Minimum",    "type": "float", "minimum": 15.0, "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 12.5,         "answer": ValidatorState.Exception}),
    ({"description": "None Maximum",         "type": "float", "minimum": 0.0,  "maximum": None,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 11.0,         "answer": ValidatorState.MaximumWarning}),
    ({"description": "None Minimum",         "type": "float", "minimum": None, "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": -1.0,         "answer": ValidatorState.MinimumWarning}),
    # Integer values
    ({"description": "Completely valid",     "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 5,            "answer": ValidatorState.Valid}),
    ({"description": "Exactly MinWarning",   "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 1,            "answer": ValidatorState.Valid}),
    ({"description": "Exactly MaxWarning",   "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 9,            "answer": ValidatorState.Valid}),
    ({"description": "Below MinWarning",     "type": "int",   "minimum": -1,   "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 0,            "answer": ValidatorState.MinimumWarning}),
    ({"description": "Above MaxWarning",     "type": "int",   "minimum": 0,    "maximum": 11,           "min_warning": 1,            "max_warning": 9,    "current": 10,           "answer": ValidatorState.MaximumWarning}),
    ({"description": "Exactly Minimum",      "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 0,            "answer": ValidatorState.MinimumWarning}),
    ({"description": "Exactly Maximum",      "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 10,           "answer": ValidatorState.MaximumWarning}),
    ({"description": "Below Minimum",        "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": -1,           "answer": ValidatorState.MinimumError}),
    ({"description": "Above Maximum",        "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 11,           "answer": ValidatorState.MaximumError}),
    ({"description": "Float precision test", "type": "int",   "minimum": 0,    "maximum": 100000,       "min_warning": 1,            "max_warning": 9,    "current": 100000,       "answer": ValidatorState.MaximumWarning}),
    ({"description": "Maximum < MaxWarning", "type": "int",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 15,   "current": 13,           "answer": ValidatorState.MaximumError}),
    ({"description": "Maximum < Minimum",    "type": "int",   "minimum": 15,   "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 13,           "answer": ValidatorState.Exception}),
    # Mixed values
    ({"description": "Completely valid",     "type": "float", "minimum": 0,    "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9,    "current": 5.0,          "answer": ValidatorState.Valid}),
    # String values
    ({"description": "Empty string valid",        "type": "str", "allow_empty": True,   "current": "",   "answer": ValidatorState.Valid}),
    ({"description": "Empty string is invalid",   "type": "str", "allow_empty": False,  "current": "",   "answer": ValidatorState.Invalid}),
    ({"description": "String is not UUID, OK",    "type": "str", "is_uuid": False,      "current": "Blorf",   "answer": ValidatorState.Valid}),
    ({"description": "String is not UUID, :-(",   "type": "str", "is_uuid": True,       "current": "Blorf",   "answer": ValidatorState.Invalid}),
    ({"description": "UUID is UUID",              "type": "str", "is_uuid": True,       "current": "123456AF-ab9d-43E6-ABcd-AB8D43e6abCD", "answer": ValidatorState.Valid}),
    ({"description": "Not match regex blacklist", "type": "str",
      "regex_blacklist_pattern": "^blacklisted value$", "current": "valid value",       "answer": ValidatorState.Valid}),
    ({"description": "Match regex blacklist",     "type": "str",
      "regex_blacklist_pattern": "^blacklisted value$", "current": "blacklisted value", "answer": ValidatorState.Invalid}),
    # Bool values
    ({"description": "No warning or error states", "type": "bool",                         "current": True,   "answer": ValidatorState.Valid}),
    ({"description": "Warning state",              "type": "bool", "warning_value": True,  "current": True,   "answer": ValidatorState.MaximumWarning}),
    ({"description": "Error state",                "type": "bool", "error_value": True,    "current": True,   "answer": ValidatorState.MaximumError}),
]

@pytest.mark.parametrize("data", test_validate_data)
def test_validate(data):
    setting_instance = MockSettingInstance(data["current"])

    setting_instance.type = data.get("type")
    setting_instance.minimum_value = data.get("minimum")
    setting_instance.maximum_value = data.get("maximum")
    setting_instance.minimum_value_warning = data.get("min_warning")
    setting_instance.maximum_value_warning = data.get("max_warning")
    setting_instance.warning_value = data.get("warning_value")
    setting_instance.error_value = data.get("error_value")
    setting_instance.allow_empty = data.get("allow_empty")
    setting_instance.is_uuid = data.get("is_uuid")
    setting_instance.regex_blacklist_pattern = data.get("regex_blacklist_pattern", "")

    validator = Validator("test")
    validation_state = validator(setting_instance) #Execute the test.

    assert validation_state == data["answer"]
