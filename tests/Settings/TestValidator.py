# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

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
        self.value = value

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
    ({"description": "Everything None",      "minimum": None, "maximum": None,         "min_warning": None,         "max_warning": None, "current": None,         "answer": ValidatorState.Exception}),
    # Floating point values
    ({"description": "Completely valid",     "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 5.0,          "answer": ValidatorState.Valid}),
    ({"description": "Exactly MinWarning",   "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 1.0,          "answer": ValidatorState.Valid}),
    ({"description": "Exactly MaxWarning",   "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 9.0,          "answer": ValidatorState.Valid}),
    ({"description": "Below MinWarning",     "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 0.5,          "answer": ValidatorState.MinimumWarning}),
    ({"description": "Above MaxWarning",     "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 9.5,          "answer": ValidatorState.MaximumWarning}),
    ({"description": "Exactly Minimum",      "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 0.0,          "answer": ValidatorState.MinimumWarning}),
    ({"description": "Exactly Maximum",      "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 10.0,         "answer": ValidatorState.MaximumWarning}),
    ({"description": "Below Minimum",        "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": -1.0,         "answer": ValidatorState.MinimumError}),
    ({"description": "Above Maximum",        "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 11.0,         "answer": ValidatorState.MaximumError}),
    ({"description": "Float precision test", "minimum": 0.0,  "maximum": 100000.0,     "min_warning": 1.0,          "max_warning": 9.0,  "current": 100000.0,     "answer": ValidatorState.MaximumWarning}),
    ({"description": "NaN value",            "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": float("nan"), "answer": ValidatorState.Exception}),
    ({"description": "NaN MinWarning",       "minimum": 0.0,  "maximum": 10.0,         "min_warning": float("nan"), "max_warning": 9.0,  "current": 1.0,          "answer": ValidatorState.Valid}),
    ({"description": "Infinity Maximum",     "minimum": 0.0,  "maximum": float("inf"), "min_warning": 1.0,          "max_warning": 9.0,  "current": 5.0,          "answer": ValidatorState.Valid}),
    ({"description": "Maximum < MaxWarning", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 15.0, "current": 12.5,         "answer": ValidatorState.MaximumError}),
    ({"description": "Maximum < Minimum",    "minimum": 15.0, "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 12.5,         "answer": ValidatorState.Exception}),
    ({"description": "None Maximum",         "minimum": 0.0,  "maximum": None,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 11.0,         "answer": ValidatorState.MaximumWarning}),
    ({"description": "None Minimum",         "minimum": None, "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": -1.0,         "answer": ValidatorState.MinimumWarning}),
    # Integer values
    ({"description": "Completely valid",     "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 5,            "answer": ValidatorState.Valid}),
    ({"description": "Exactly MinWarning",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 1,            "answer": ValidatorState.Valid}),
    ({"description": "Exactly MaxWarning",   "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 9,            "answer": ValidatorState.Valid}),
    ({"description": "Below MinWarning",     "minimum": -1,   "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 0,            "answer": ValidatorState.MinimumWarning}),
    ({"description": "Above MaxWarning",     "minimum": 0,    "maximum": 11,           "min_warning": 1,            "max_warning": 9,    "current": 10,           "answer": ValidatorState.MaximumWarning}),
    ({"description": "Exactly Minimum",      "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 0,            "answer": ValidatorState.MinimumWarning}),
    ({"description": "Exactly Maximum",      "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 10,           "answer": ValidatorState.MaximumWarning}),
    ({"description": "Below Minimum",        "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": -1,           "answer": ValidatorState.MinimumError}),
    ({"description": "Above Maximum",        "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 11,           "answer": ValidatorState.MaximumError}),
    ({"description": "Float precision test", "minimum": 0,    "maximum": 100000,       "min_warning": 1,            "max_warning": 9,    "current": 100000,       "answer": ValidatorState.MaximumWarning}),
    ({"description": "Maximum < MaxWarning", "minimum": 0,    "maximum": 10,           "min_warning": 1,            "max_warning": 15,   "current": 13,           "answer": ValidatorState.MaximumError}),
    ({"description": "Maximum < Minimum",    "minimum": 15,   "maximum": 10,           "min_warning": 1,            "max_warning": 9,    "current": 13,           "answer": ValidatorState.Exception}),
    # Mixed values
    ({"description": "Completely valid",     "minimum": 0,    "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9,    "current": 5.0,          "answer": ValidatorState.Valid}),
]

@pytest.mark.parametrize("data", test_validate_data)
def test_validate(data):
    setting_instance = MockSettingInstance(data["current"])
    setting_instance.minimum_value = data["minimum"]
    setting_instance.maximum_value = data["maximum"]
    setting_instance.minimum_value_warning = data["min_warning"]
    setting_instance.maximum_value_warning = data["max_warning"]

    validator = Validator("test")
    validation_state = validator(setting_instance) #Execute the test.

    assert validation_state == data["answer"]
