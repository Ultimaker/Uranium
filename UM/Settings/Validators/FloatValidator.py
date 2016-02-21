# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Settings.Validators.Validator import Validator
from UM.Settings.Validators.ResultCodes import ResultCodes

## Validates if a setting is within two possible ranges (error range & warning range) and if setting is integer.
class FloatValidator(Validator):
    def __init__(self, setting, min_value = None, max_value = None, min_value_warning = None, max_value_warning = None):
        super(FloatValidator,self).__init__(setting)   
        self._min_value = min_value
        self._max_value = max_value
        self._min_value_warning = min_value_warning
        self._max_value_warning = max_value_warning
    
    def setRange(self, min_value = None, max_value = None, min_value_warning = None , max_value_warning = None):
        self._min_value = min_value
        self._max_value = max_value
        self._min_value_warning = min_value_warning
        self._max_value_warning = max_value_warning
    
    def setMinValue(self, min_value):
        self._min_value = min_value

    def setMaxValue(self, max_value):
        self._max_value = max_value

    def setMaxValueWarning(self, max_value_warning):
        self._max_value_warning = max_value_warning

    def setMinValueWarning(self, min_value_warning):
        self._min_value_warning = min_value_warning

    ## Validate the setting. 
    # \returns result Returns value as defined in ResultCodes.py
    # \returns message Message providing more detail about warning / error (if any)
    def validate(self, value):
        try:
            return self._checkRange(float(value), self._min_value, self._max_value, self._min_value_warning, self._max_value_warning)
        except (ValueError, SyntaxError, TypeError, NameError) as e:
            return ResultCodes.not_valid_error
