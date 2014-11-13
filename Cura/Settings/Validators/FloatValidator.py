from Cura.Settings.Validators.Validator import Validator

## Validator to check if the provided value is a valid float and within min_value and max_value. 
class FloatValidator(Validator):
    def __init__(self, setting, min_value = None, max_value = None):
        super(FloatValidator,self).__init__(setting)   
        self._min_value = min_value
        self._max_value = max_value
    
    ## Validate the setting. 
    # \returns result Returns 0 on succes, 1 on warning and 2 on error
    # \returns message Message providing more detail about warning / error (if any)
    def validate(self):
        try:
            f = float(eval(self._setting.getValue().replace(',','.'), {}, {}))
            if self._min_value is not None and f < self._min_value:
                return self._error_code , 'This setting should not be below ' + str(round(self._min_value, 3))
            if self._max_value is not None and f > self._max_value:
                return self._error_code , 'This setting should not be above ' + str(self._max_value)
            return self._succes_code, ''
        except (ValueError, SyntaxError, TypeError, NameError):
            return self._error_code , '"' + str(self._setting.getValue()) + '" is not a valid number or expression'