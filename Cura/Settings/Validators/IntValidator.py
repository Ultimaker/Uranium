from Cura.Settings.Validators.Validator import Validator

class IntValidator(Validator):
    def __init__(self, setting, min_value = None, max_value = None):
        super(IntValidator,self).__init__(setting)   
        self._min_value = min_value
        self._max_value = max_value
    
    def validate(self):
        try:
            f = int(eval(self._setting.getValue(), {}, {}))
            if self._min_value is not None and f < self._min_value:
                return self._error_code, 'This setting should not be below ' + str(self._min_value)
            if self._max_value is not None and f > self._max_value:
                return self._error_code, 'This setting should not be above ' + str(self._max_value)
            return self._succes_code, ''
        except (ValueError, SyntaxError, TypeError, NameError):
            return self._error_code, '"' + str(self._setting.getValue()) + '" is not a valid whole number or expression'