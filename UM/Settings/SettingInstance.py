# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import copy
import enum
from typing import Any, cast, Dict, Iterable, Optional

from UM.Settings.Interfaces import ContainerInterface
from UM.Logging.Logger import Logger
from UM.Settings.Validator import Validator

from .SettingFunction import SettingFunction
from .SettingDefinition import SettingDefinition


##  The state of the instance
#
#   This enum describes which state the instance is in. The state describes
#   how the instance got its value.
class InstanceState(enum.IntEnum):
    Default = 1  ## Default state, no value has been set.
    Calculated = 2  ## Value is the result of calculations in a SettingFunction object.
    User = 3  ## Value is the result of direct user interaction.


##  Encapsulates all state of a setting.
#
#   The SettingInstance class contains all state related to a setting.
class SettingInstance:
    ##  Constructor.
    #
    #   \param definition The SettingDefinition object this is an instance of.
    #   \param container The container of this instance. Needed for relation handling.
    def __init__(self, definition: SettingDefinition, container: ContainerInterface, *args: Any, **kwargs: Any) -> None:
        if container is None:
            raise ValueError("Cannot create a setting instance without a container")

        super().__init__()

        self._definition = definition  # type: SettingDefinition
        self._container = container  # type: ContainerInterface

        self._visible = True  # type: bool
        self._validator = None  # type: Optional[Validator]
        validator_type = SettingDefinition.getValidatorForType(self._definition.type)
        if validator_type:
            self._validator = validator_type(self._definition.key)

        self._state = InstanceState.Default

        self.__property_values = {}  # type: Dict[str, Any]

    ##  Get a list of all supported property names
    def getPropertyNames(self) -> Iterable[str]:
        return self.__property_values.keys()

    ##  Copies the setting instance and all its properties and state.
    #
    #   The definition and the instance container containing this instance are
    #   not deep-copied but just taken over from the original, since they are
    #   seen as back-links. Please set them correctly after deep-copying this
    #   instance.
    def __deepcopy__(self, memo: Dict[int, Dict[str, Any]]) -> "SettingInstance":
        result = SettingInstance(self._definition, self._container)
        result._visible = self._visible
        result._validator = copy.deepcopy(self._validator, memo) #type: ignore #I give up trying to get the type of deepcopy argument 1 right.
        result._state = self._state
        result.__property_values = copy.deepcopy(self.__property_values, memo)
        return result

    def __eq__(self, other: object) -> bool:
        if type(self) != type(other):
            return False  # Type mismatch
        other = cast(SettingInstance, other)

        for property_name in self.__property_values:
            try:
                if other.__getattr__(property_name) != self.__getattr__(property_name):
                    return False  # Property values don't match
            except AttributeError:
                return False  # Other does not have the property
        return True

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __getattr__(self, name: str) -> Any:
        if name == "_SettingInstance__property_values":
            # Prevent infinite recursion when __property_values is not set.
            # This happens primarily with Pickle
            raise AttributeError("'SettingInstance' object has no attribute '{0}'".format(name))

        if name in self.__property_values:
            value = self.__property_values[name]
            if isinstance(value, str) and name == "value":
                try:
                    return SettingDefinition.settingValueFromString(self._definition.type, value)
                except Exception:
                    return value
            else:
                return value

        raise AttributeError("'SettingInstance' object has no attribute '{0}'".format(name))

    def setProperty(self, name: str, value: Any) -> None:
        if SettingDefinition.hasProperty(name):
            if SettingDefinition.isReadOnlyProperty(name):
                Logger.log("e", "Tried to set property %s which is a read-only property", name)
                return

            if name not in self.__property_values or value != self.__property_values[name]:
                if isinstance(value, str) and value.strip().startswith("="):
                    value = SettingFunction(value[1:])

                self.__property_values[name] = value
                if name == "value":
                    self._state = InstanceState.User

        else:
            if name == "state":
                if value == "InstanceState.Calculated":
                    self._state = InstanceState.Calculated
            else:
                raise AttributeError("No property {0} defined".format(name))

    @property
    def definition(self) -> SettingDefinition:
        return self._definition

    @property
    def container(self) -> ContainerInterface:
        return self._container

    @property
    def validationState(self) -> Optional[Validator]:
        return self._validator

    @property
    def state(self) -> InstanceState:
        return self._state

    def resetState(self) -> None:
        self._state = InstanceState.Default

    def __repr__(self) -> str:
        return "<SettingInstance (0x{0:x}) definition={1} container={2}>".format(id(self), self._definition, self._container)
