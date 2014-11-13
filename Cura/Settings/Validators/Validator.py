class Validator(object):
    def __init__(self, setting):
        self._setting = setting
        self._setting.setValidator(self)
    
    def getSetting(self):
        return self._setting
    
    def validate(self):
        raise NotImplementedError('Validator was not correctly implemented')
    
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