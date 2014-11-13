class Validator(object):
    def __init__(self, setting):
        self.setting._validators.append(self)
        self._setting = setting
        self._succes_code = 0
        self._warning_code = 1
        self._error_code = 2
    
    def getSetting(self):
        return self._setting
    
    def validate(self):
        raise NotImplementedError('Validator was not correctly implemented')