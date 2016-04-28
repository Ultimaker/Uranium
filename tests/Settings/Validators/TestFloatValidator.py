# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest

from UM.Settings.Validators.FloatValidator import FloatValidator
from UM.Settings.Validator import ValidatorState

##  Fake setting instance that stands in for the real setting instance.
#
#   If anything should go wrong in the real setting instance, it won't
#   influence the unit tests for the float validator.
class MockSettingInstance:
    ##  Creates the mock setting instance.
    def __init__(self, value):
        self.value = value

    ##  Gets the value of this setting instance.
    def getValue(self):
        return self.value

##  Called before the first test function is executed.
@pytest.fixture
def validator():
    setting_instance = MockSettingInstance(0)
    return FloatValidator(setting_instance)

##  Tests the creation of a float validator.
def test_createFloatValidator(validator):
    assert validator.getState() == ValidatorState.Unknown

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
    ({"description": "NaN MinWarning",       "minimum": 0.0,  "maximum": 10.0,         "min_warning": float("nan"), "max_warning": 9.0,  "current": 5.0,          "answer": ValidatorState.Exception}),
    ({"description": "Infinity Maximum",     "minimum": 0.0,  "maximum": float("inf"), "min_warning": 1.0,          "max_warning": 9.0,  "current": 5.0,          "answer": ValidatorState.Valid}),
    ({"description": "Maximum < MaxWarning", "minimum": 0.0,  "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 15.0, "current": 12.5,         "answer": ValidatorState.MaximumError}),
    ({"description": "Maximum < Minimum",    "minimum": 15.0, "maximum": 10.0,         "min_warning": 1.0,          "max_warning": 9.0,  "current": 12.5,         "answer": ValidatorState.Exception})
]

@pytest.mark.parametrize("data", test_validate_data)
def test_validate(data):
    setting_instance = MockSettingInstance(data["current"])
    validator = FloatValidator(setting_instance)
    validator.setMinimum(data["minimum"])
    validator.setMaximum(data["maximum"])
    validator.setMinimumWarning(data["min_warning"])
    validator.setMaximumWarning(data["max_warning"])

    validator.validate() #Execute the test.

    assert validator.getState() == data["answer"]