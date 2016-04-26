# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

##  Encapsulates Python code that provides a simple value calculation function.
#
class SettingFunction:
    ##  Constructor.
    #
    #   \param code The Python code this function should evaluate.
    def __init__(self, code, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._code = code
        self._settings = []

    ##  Call the actual function to calculate the value.
    def __call__(self, *args, **kwargs):
        pass

    def __eq__(self, other):
        if not isinstance(other, SettingFunction):
            return False

        return self._code == other._code

    ##  Retrieve a list of the keys of all the settings used in this function.
    def getUsedSettings(self):
        return self._settings
