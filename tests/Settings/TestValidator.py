# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import sys

#from UM.Settings.Validators.FloatValidator import FloatValidator
from UM.Settings.Validator import Validator, ValidatorState
from UM.Signal import Signal

##  Fake setting instance that stands in for the real setting instance.
#
#   If anything should go wrong in the real setting instance, it won't
#   influence the unit tests for the float validator.
class MockSettingInstance:
    ##  Creates the mock setting instance.
    def __init__(self, value):
        self.minimum_value = sys.float_info.min
        self.maximum_value = sys.float_info.max
        self.minimum_value_warning = sys.float_info.min
        self.maximum_value_warning = sys.float_info.max
        self.value = value

    propertyChanged = Signal()

##  Called before the first test function is executed.
@pytest.fixture
def validator():
    setting_instance = MockSettingInstance(0)
    return Validator(setting_instance)

##  Tests the creation of a float validator.
#
#   \param validator A new validator from a fixture.
def test_create(validator):
    assert validator.state == ValidatorState.Unknown

###  Tests the changing of the maximum value.
##
##   \param validator A new validator from a fixture.
#def test_setMaximum(validator):
    #validator.validate() # To set the state to something else than Unknown.
    #validator.setMaximum(3.14156)
    #assert validator.getState() == ValidatorState.Unknown
    #assert validator.getMaximum() == 3.14156

###  Tests the changing of the maximum warning value.
##
##   \param validator A new validator from a fixture.
#def test_setMaximumWarning(validator):
    #validator.validate() # To set the state to something else than Unknown.
    ##validator.setMaximumWarning(3.14156)
    #assert validator.getState() == ValidatorState.Unknown
    ##assert validator.getMaximumWarning() == 3.14156

###  Tests the changing of the minimum value.
##
##   \param validator A new validator from a fixture.
#def test_setMinimum(validator):
    #validator.validate() # To set the state to something else than Unknown.
    ##validator.setMinimum(3.14156)
    #assert validator.state == ValidatorState.Unknown
    ##assert validator.getMinimum() == 3.14156

###  Tests the changing of the minimum warning value.
##
##   \param validator A new validator from a fixture.
#def test_setMinimumWarning(validator):
    ##validator.validate() # To set the state to something else than Unknown.
    ##validator.setMinimumWarning(3.14156)
    #assert validator.state == ValidatorState.Unknown
    ##assert validator.getMinimumWarning() == 3.14156

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
    validator = Validator(setting_instance)
    setting_instance.minimum_value = data["minimum"]
    setting_instance.maximum_value = data["maximum"]
    setting_instance.minimum_value_warning = data["min_warning"]
    setting_instance.maximum_value_warning = data["max_warning"]

    validator.validate() #Execute the test.

    assert validator.state == data["answer"]
