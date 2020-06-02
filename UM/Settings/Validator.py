# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from enum import Enum
import re
from typing import Optional
import uuid

from UM.Settings.Interfaces import ContainerInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext
from UM.Logger import Logger

from . import SettingFunction


class ValidatorState(Enum):
    Exception = "Exception"
    Unknown = "Unknown"
    Valid = "Valid"
    Invalid = "Invalid"
    MinimumError = "MinimumError"
    MinimumWarning = "MinimumWarning"
    MaximumError = "MaximumError"
    MaximumWarning = "MaximumWarning"


class Validator(SettingFunction.SettingFunction):
    """Validates that a SettingInstance's value is within a certain minimum and maximum value.

    This class performs validation of any value that has __lt__ and __gt__ implemented, but
    it is primarily used for numerical values like integers and floats.
    """

    def __init__(self, key: str) -> None:
        """Constructor

        :param instance: The instance this Validator validates.
        """

        if key is None:
            raise ValueError("Instance should not be None")

        super().__init__("None")

        self._key = key  # type: str

    def __call__(self, value_provider: ContainerInterface, context: Optional[PropertyEvaluationContext] = None) -> Optional[ValidatorState]:
        """Perform the actual validation."""

        if not value_provider:
            return None

        state = ValidatorState.Unknown
        try:
            allow_empty = value_provider.getProperty(self._key, "allow_empty", context = context)  # For string only
            is_uuid = value_provider.getProperty(self._key, "is_uuid", context = context)  # For string only
            regex_blacklist_pattern = value_provider.getProperty(self._key, "regex_blacklist_pattern", context = context)  # For string only
            minimum = value_provider.getProperty(self._key, "minimum_value", context = context)
            maximum = value_provider.getProperty(self._key, "maximum_value", context = context)
            minimum_warning = value_provider.getProperty(self._key, "minimum_value_warning", context = context)
            maximum_warning = value_provider.getProperty(self._key, "maximum_value_warning", context = context)

            # For boolean
            boolean_warning_value = value_provider.getProperty(self._key, "warning_value", context = context)
            boolean_error_value = value_provider.getProperty(self._key, "error_value", context = context)

            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError("Cannot validate a state of setting {0} with minimum > maximum".format(self._key))

            if context is not None:
                value_provider = context.rootStack()

            value = value_provider.getProperty(self._key, "value", context = context)
            if value is None or value != value:
                raise ValueError("Cannot validate None, NaN or similar values in setting {0}, actual value: {1}".format(self._key, value))

            setting_type = value_provider.getProperty(self._key, "type", context = context)

            if setting_type == "str":
                # "allow_empty is not None" is not necessary here because of "allow_empty is False", but it states
                # explicitly that we should not do this check when "allow_empty is None".
                if allow_empty is not None and allow_empty is False and str(value) == "":
                    state = ValidatorState.Invalid
                    return state

                if is_uuid is not None and is_uuid is True:
                    # Try to parse the UUID string with uuid.UUID(). It will raise a ValueError if it's not valid.
                    try:
                        uuid.UUID(str(value))
                        state = ValidatorState.Valid
                    except ValueError:
                        state = ValidatorState.Invalid
                    return state

                # If "regex_blacklist_pattern" is set, it will be used to validate the value string. If the value string
                # matches the blacklist pattern, the value will be invalid.
                if regex_blacklist_pattern is not None and len(regex_blacklist_pattern) > 0:
                    regex = re.compile(regex_blacklist_pattern)
                    is_valid = regex.fullmatch(str(value).lower()) is None
                    state = ValidatorState.Valid if is_valid else ValidatorState.Invalid
                    return state

                state = ValidatorState.Valid
                return state

            elif setting_type == "bool":
                state = ValidatorState.Valid
                if boolean_warning_value is not None and value == boolean_warning_value:
                    state = ValidatorState.MaximumWarning
                elif boolean_error_value is not None and value == boolean_error_value:
                    state = ValidatorState.MaximumError

            elif minimum is not None and value < minimum:
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
