# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from enum import Enum
from typing import Any

from UM.Settings.Interfaces import ContainerInterface
from UM.Logger import Logger

MYPY = False
if MYPY:
    from UM.Settings.SettingInstance import SettingInstance

from . import SettingFunction

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
class Validator(SettingFunction.SettingFunction):
    ##  Constructor
    #
    #   \param instance The instance this Validator validates.
    def __init__(self, key: str) -> None:
        if key is None:
            raise ValueError("Instance should not be None")

        super().__init__("None")

        self._key = key  # type: str

    ##  Perform the actual validation.
    def __call__(self, value_provider: ContainerInterface) -> Any:
        if not value_provider:
            return

        state = ValidatorState.Unknown
        try:
            minimum = value_provider.getProperty(self._key, "minimum_value")
            maximum = value_provider.getProperty(self._key, "maximum_value")
            minimum_warning = value_provider.getProperty(self._key, "minimum_value_warning")
            maximum_warning = value_provider.getProperty(self._key, "maximum_value_warning")

            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError("Cannot validate a state of setting {0} with minimum > maximum".format(self._key))

            value = value_provider.getProperty(self._key, "value")
            if value is None or value != value:
                raise ValueError("Cannot validate None, NaN or similar values in setting {0}, actual value: {1}".format(self._key, value))

            if minimum is not None and value < minimum:
                state = ValidatorState.MinimumError
            elif maximum is not None and value > maximum:
                state = ValidatorState.MaximumError
            elif minimum_warning is not None and value < minimum_warning:
                state = ValidatorState.MinimumWarning
            elif maximum_warning is not None and value > maximum_warning:
                state = ValidatorState.MaximumWarning
            else:
                state = ValidatorState.Valid
        except:
            Logger.logException("w", "Could not validate setting %s, an exception was raised", self._key)
            state = ValidatorState.Exception

        return state
