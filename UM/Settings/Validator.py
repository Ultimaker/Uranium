# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

##  Validates that a SettingInstance's value is within a certain minimum and maximum value.
#
#
class Validator:
    ##  Constructor
    #
    #   \param instance The instance this Validator validates.
    def __init__(self, instance, *args, **kwargs):
        if instance is None:
            raise ValueError("Instance should not be None")

        super().__init__(*args, **kwargs)

        self._instance = instance

    def getMinimum(self):
        pass

    def getMaximum(self):
        pass

    def getMinimumWarning(self):
        pass

    def getMaximumWarning(self):
        pass

    def validate(self):
        pass
