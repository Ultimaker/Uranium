# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from enum import Enum

class ValidatorState(Enum):
    Exception = "Exception"
    Unknown = "Unknown"
    Valid = "Valid"
    MinimumError = "MinimumError"
    MinimumWarning = "MinimumWarning"
    MaximumError = "MaximumError"
    MaximumWarning = "MaximumWarning"

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

    ##  Changes the maximum allowed value for this validator.
    #
    #   If the value of the setting instance exceeds this value, the state of
    #   the validator should become MaximumError.
    #
    #   \param maximum The new maximum value.
    def setMaximum(self, maximum):
        pass

    ##  Changes the maximum value before a warning is given for this validator.
    #
    #   If the value of the setting instance exceeds this value, the state of
    #   the validator should become MaximumWarning, unless it exceeds the
    #   maximum value too.
    #
    #   \param maximum_warning The new maximum warning value.
    def setMaximumWarning(self, maximum_warning):
        pass

    ##  Changes the minimum allowed value for this validator.
    #
    #   If the value of the setting instance is lower than this value, the state
    #   of the validator should become MinimumError.
    #
    #   \param minimum The new minimum value.
    def setMinimum(self, minimum):
        pass

    ##  Changes the minimum value before a warning is given for this validator.
    #
    #   If the value of the setting instance is lower than this value, the state
    #   of the validator should become MinimumWarning, unless it exceeds the
    #   minimum value too.
    #
    #   \param minimum_warning The new minimum warning value.
    def setMinimumWarning(self, minimum_warning):
        pass

    def validate(self):
        pass
