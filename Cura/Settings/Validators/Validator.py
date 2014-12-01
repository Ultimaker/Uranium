#  Abstract class
## Base class for a setting validator. Each validator is tied to a single setting. 
#  They can have a minimum & maximum value as well as a minimum & maximum warning value.
# TODO: The validators are not yet used to validate any settings.
from Cura.Settings.Validators.ResultCodes import ResultCodes
class Validator(object):
    def __init__(self, setting):
        self._setting = setting
        self._setting.setValidator(self)
    
    ## Get the setting that this validator is watching.
    # \returns Setting
    def getSetting(self):
        return self._setting
    
    ## Do the validation.
    def validate(self):
        raise NotImplementedError('Validator was not correctly implemented')
    
    ## Check if provided value is within range. 
    # \param value The value to be checked
    # \param min_value The minimum value the value must have. If it's exceded, return error.
    # \param max_value The max value the value must have. If it's exceded, return error.
    # \param min_value_warning The min value the value can have. If it's exceded, return warning.
    # \param max_value_warning The max value the value can have. If it's exceded, return warning.
    # \returns Succes code if it is within range. Warnings / errors if either bounds are not met.
    def _checkRange(self, value, min_value, max_value, min_value_warning, max_value_warning):
        if min_value is not None and value < min_value:
            return ResultCodes.min_value_error
        if max_value is not None and value > max_value:
            return ResultCodes.min_value_error
        
        if min_value_warning is not None and value < min_value_warning:
            return ResultCodes.min_value_warning
        if max_value_warning is not None and value > max_value_warning:
            return ResultCodes.max_value_warning
        
        return ResultCodes.succes
    