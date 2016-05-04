# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from enum import Enum

from UM.Logger import Logger

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
#   This class performs validation of any value that has __lt__ and __gt__ implemented, but
#   it is primarily used for numerical values like integers and floats.
class Validator:
    ##  Constructor
    #
    #   \param instance The instance this Validator validates.
    def __init__(self, instance, *args, **kwargs):
        if instance is None:
            raise ValueError("Instance should not be None")

        super().__init__(*args, **kwargs)

        self._instance = instance
        self._state = ValidatorState.Unknown

    @property
    def state(self):
        return self._state

    ##  Perform the actual validation.
    def validate(self):
        self._state = ValidatorState.Unknown
        try:
            minimum = None
            if hasattr(self._instance, "minimum_value"):
                minimum = self._instance.minimum_value
            maximum = None
            if hasattr(self._instance, "maximum_value"):
                maximum = self._instance.maximum_value
            minimum_warning = None
            if hasattr(self._instance, "minimum_value_warning"):
                minimum_warning = self._instance.minimum_value_warning
            maximum_warning = None
            if hasattr(self._instance, "maximum_value_warning"):
                maximum_warning = self._instance.maximum_value_warning

            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError("Cannot validate a state with minimum > maximum")

            # If we have no value property, just do nothing
            if not hasattr(self._instance, "value"):
                self._state = ValidatorState.Unknown
                return

            value = self._instance.value
            if value is None or value != value:
                raise ValueError("Cannot validate None, NaN or similar values")

            if minimum is not None and value < minimum:
                self._state = ValidatorState.MinimumError
            elif maximum is not None and value > maximum:
                self._state = ValidatorState.MaximumError
            elif minimum_warning is not None and value < minimum_warning:
                self._state = ValidatorState.MinimumWarning
            elif maximum_warning is not None and value > maximum_warning:
                self._state = ValidatorState.MaximumWarning
            else:
                self._state = ValidatorState.Valid
        except Exception as e:
            Logger.logException("w", "Could not validate, an exception was raised")
            self._state = ValidatorState.Exception
