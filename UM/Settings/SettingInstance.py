# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import copy #To implement deepcopy.
import enum
import os
from typing import Any, cast, Dict, Iterable, List, Optional, Set, TYPE_CHECKING

from UM.Settings.Interfaces import ContainerInterface
from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.Decorators import call_if_enabled
from UM.Settings.Validator import Validator #For typing.

if TYPE_CHECKING:
    from UM.Settings.SettingRelation import SettingRelation
from UM.Settings.SettingRelation import RelationType
from . import SettingFunction
from .SettingDefinition import SettingDefinition

# Helper functions for SettingInstance tracing
def _traceSetProperty(instance: "SettingInstance", property_name: str, property_value: Any, container: ContainerInterface) -> None:
    Logger.log("d", "Set property '{0}' of '{1}' to '{2}', updating using values from {3}".format(property_name, instance, property_value, container))

def _traceUpdateProperty(instance: "SettingInstance", property_name: str, container: ContainerInterface) -> None:
    Logger.log("d", "Updating property '{0}' of '{1}' using container {2}".format(property_name, instance, container))

def _traceRelations(instance: "SettingInstance", container: ContainerInterface) -> None:
    Logger.log("d", "Updating relations of '{0}'", instance)

    property_names = SettingDefinition.getPropertyNames()
    property_names.remove("value")  # Move "value" to the front of the list so we always update that first.
    property_names.insert(0, "value")

    for property_name in property_names:
        if SettingDefinition.isReadOnlyProperty(property_name):
            continue

        changed_relations = set()   # type: Set[SettingRelation]
        instance._addRelations(changed_relations, instance.definition.relations, [property_name])

        for relation in changed_relations:
            Logger.log("d", "Emitting property change for relation {0}", relation)
            #container.propertyChanged.emit(relation.target.key, relation.role)
            # If the value/minimum value/etc state is updated, the validation state must be re-evaluated
            if relation.role in {"value", "minimum_value", "maximum_value", "minimum_value_warning", "maximum_value_warning"}:
                Logger.log("d", "Emitting validationState changed for {0}", relation)
                container.propertyChanged.emit(relation.target.key, "validationState")

def _isTraceEnabled() -> bool:
    return "URANIUM_TRACE_SETTINGINSTANCE" in os.environ


class InstanceState(enum.IntEnum):
    """The state of the instance

    This enum describes which state the instance is in. The state describes
    how the instance got its value.
    """

    Default = 1  ## Default state, no value has been set.
    Calculated = 2  ## Value is the result of calculations in a SettingFunction object.
    User = 3  ## Value is the result of direct user interaction.


@signalemitter
class SettingInstance:
    """Encapsulates all state of a setting.

    The SettingInstance class contains all state related to a setting.
    """

    def __init__(self, definition: SettingDefinition, container: ContainerInterface, *args: Any, **kwargs: Any) -> None:
        """Constructor.

        :param definition: The SettingDefinition object this is an instance of.
        :param container: The container of this instance. Needed for relation handling.
        """

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

    def getPropertyNames(self) -> Iterable[str]:
        """Get a list of all supported property names"""

        return self.__property_values.keys()

    def __deepcopy__(self, memo: Dict[int, Dict[str, Any]]) -> "SettingInstance":
        """Copies the setting instance and all its properties and state.

        The definition and the instance container containing this instance are not deep-copied but just taken over from
        the original, since they are seen as back-links. Please set them correctly after deep-copying this instance.
        """

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

        # Check if the other has properties that self doesn't have.
        for property_name in other.getPropertyNames():
            if property_name not in self.__property_values:
                return False
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

    @call_if_enabled(_traceSetProperty, _isTraceEnabled())
    def setProperty(self, name: str, value: Any, container: Optional[ContainerInterface] = None, emit_signals: bool = True) -> None:
        if SettingDefinition.hasProperty(name):
            if SettingDefinition.isReadOnlyProperty(name):
                Logger.log("e", "Tried to set property %s which is a read-only property", name)
                return

            if name not in self.__property_values or value != self.__property_values[name]:
                if isinstance(value, str) and value.strip().startswith("="):
                    value = SettingFunction.SettingFunction(value[1:])

                self.__property_values[name] = value
                if name == "value":
                    if not container:
                        container = self._container
                    ## If state changed, emit the signal
                    if self._state != InstanceState.User:
                        self._state = InstanceState.User
                        if emit_signals:
                            self.propertyChanged.emit(self._definition.key, "state")

                    self.updateRelations(container, emit_signals = emit_signals)

                if self._validator and emit_signals:
                    self.propertyChanged.emit(self._definition.key, "validationState")

                if emit_signals:
                    self.propertyChanged.emit(self._definition.key, name)
                for property_name in self._definition.getPropertyNames():
                    if self._definition.dependsOnProperty(property_name) == name:
                        if emit_signals:
                            self.propertyChanged.emit(self._definition.key, property_name)
        else:
            if name == "state":
                if value == "InstanceState.Calculated":
                    if self._state != InstanceState.Calculated:
                        self._state = InstanceState.Calculated
                        if emit_signals:
                            self.propertyChanged.emit(self._definition.key, "state")
            else:
                raise AttributeError("No property {0} defined".format(name))

    propertyChanged = Signal()
    """Emitted whenever a property of this instance changes.

    :param instance: The instance that reported the property change (usually self).
    :param property: The name of the property that changed.
    """

    @property
    def definition(self) -> SettingDefinition:
        """The SettingDefinition this instance maintains state for."""

        return self._definition

    @property
    def container(self) -> ContainerInterface:
        """The container of this instance."""

        return self._container

    @property
    def validationState(self) -> Optional[Validator]:
        """Get the state of validation of this instance."""

        return self._validator

    @property
    def state(self) -> InstanceState:
        return self._state

    def resetState(self) -> None:
        self._state = InstanceState.Default

    def __repr__(self) -> str:
        return "<SettingInstance (0x{0:x}) definition={1} container={2}>".format(id(self), self._definition, self._container)

    @call_if_enabled(_traceRelations, _isTraceEnabled())
    def updateRelations(self, container: ContainerInterface, emit_signals: bool = True) -> None:
        """protected:"""

        property_names = SettingDefinition.getPropertyNames()
        property_names.remove("value")  # Move "value" to the front of the list so we always update that first.
        property_names.insert(0, "value")

        for property_name in property_names:
            if SettingDefinition.isReadOnlyProperty(property_name):
                continue

            changed_relations = set()   # type: Set[SettingRelation]
            self._addRelations(changed_relations, self._definition.relations, [property_name])

            # TODO: We should send this as a single change event instead of several of them.
            # That would increase performance by reducing the amount of updates.
            if emit_signals:
                for relation in changed_relations:
                    container.propertyChanged.emit(relation.target.key, relation.role)
                    # If the value/minimum value/etc state is updated, the validation state must be re-evaluated
                    if relation.role in {"value", "minimum_value", "maximum_value", "minimum_value_warning", "maximum_value_warning"}:
                        container.propertyChanged.emit(relation.target.key, "validationState")

    def _addRelations(self, relations_set: Set["SettingRelation"], relations: List["SettingRelation"], roles: List[str]) -> None:
        """Recursive function to put all settings that require eachother for changes of a property value in a list

        :param relations_set: :type{set} Set of keys (strings) of settings that are influenced
        :param relations: list of relation objects that need to be checked.
        :param roles: list of name of the properties value of the settings
        """

        for relation in filter(lambda r: r.role in roles, relations):
            if relation.type == RelationType.RequiresTarget:
                continue

            # Do not add relation to self.
            if relation.target.key == self.definition.key:
                continue

            # Don't add it to list if it's already there.
            # We do need to continue, as it might cause recursion issues otherwise.
            if relation in relations_set:
                continue

            relations_set.add(relation)

            property_names = SettingDefinition.getPropertyNames()
            property_names.remove("value")  # Move "value" to the front of the list so we always update that first.
            property_names.insert(0, "value")

            self._addRelations(relations_set, relation.target.relations, property_names)
