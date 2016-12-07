# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import enum
import os

from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.Decorators import call_if_enabled

from . import SettingRelation
from . import Validator
from . import SettingFunction
from .SettingDefinition import SettingDefinition

# Helper functions for SettingInstance tracing
def _traceSetProperty(instance, property_name, property_value, container):
    Logger.log("d", "Set property '{0}' of '{1}' to '{2}', updating using values from {3}".format(property_name, instance, property_value, container))

def _traceUpdateProperty(instance, property_name, container):
    Logger.log("d", "Updating property '{0}' of '{1}' using container {2}".format(property_name, instance, container))

def _isTraceEnabled():
    return "URANIUM_TRACE_SETTINGINSTANCE" in os.environ


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
@signalemitter
class SettingInstance:
    ##  Constructor.
    #
    #   \param definition The SettingDefinition object this is an instance of.
    #   \param container The container of this instance. Needed for relation handling.
    def __init__(self, definition, container, *args, **kwargs):
        if container is None:
            raise ValueError("Cannot create a setting instance without a container")

        super().__init__(*args, **kwargs)

        self._definition = definition
        self._container = container

        self._visible = True
        self._validator = None
        validator_type = SettingDefinition.getValidatorForType(self._definition.type)
        if validator_type:
            self._validator = validator_type(self._definition.key)

        self._state = InstanceState.Default

        self.__property_values = {}

    ##  Get a list of all supported property names
    def getPropertyNames(self):
        return self.__property_values.keys()

    def __eq__(self, other):
        if type(self) != type(other):
            return False  # Type mismatch

        for property_name in self.__property_values:
            try:
                if other.__getattr__(property_name) != self.__getattr__(property_name):
                    return False  # Property values don't match
            except AttributeError:
                return False  # Other does not have the property
        return True

    def __ne__(self, other):
        return not (self == other)

    def __getattr__(self, name):
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
    def setProperty(self, name, value, container = None):
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
                        self.propertyChanged.emit(self._definition.key, "state")

                    self.updateRelations(container)

                if self._validator:
                    self.propertyChanged.emit(self._definition.key, "validationState")

                self.propertyChanged.emit(self._definition.key, name)
                for property_name in self._definition.getPropertyNames():
                    if self._definition.dependsOnProperty(property_name) == name:
                        self.propertyChanged.emit(self._definition.key, property_name)
        else:
            if name == "state":
                if value == "InstanceState.Calculated":
                    if self._state != InstanceState.Calculated:
                        self._state = InstanceState.Calculated
                        self.propertyChanged.emit(self._definition.key, "state")
            else:
                raise AttributeError("No property {0} defined".format(name))

    @call_if_enabled(_traceUpdateProperty, _isTraceEnabled())
    def updateProperty(self, name, container = None):
        if not SettingDefinition.hasProperty(name):
            Logger.log("e", "Trying to update unknown property %s", name)
            return

        if name == "value" and self._state == InstanceState.User:
            Logger.log("d", "Ignoring update of value for setting %s since it has been set by the user.", self._definition.key)
            return

        if self._validator:
            self.propertyChanged.emit(self._definition.key, "validationState")

        self.propertyChanged.emit(self._definition.key, name)

    ##  Emitted whenever a property of this instance changes.
    #
    #   \param instance The instance that reported the property change (usually self).
    #   \param property The name of the property that changed.
    propertyChanged = Signal()

    ##  The SettingDefinition this instance maintains state for.
    @property
    def definition(self):
        return self._definition

    ##  The container of this instance.
    @property
    def container(self):
        return self._container

    ##  Get the state of validation of this instance.
    @property
    def validationState(self):
        if self._validator:
            return self._validator

        return None

    @property
    def state(self):
        return self._state

    def resetState(self):
        self._state = InstanceState.Default

    def __repr__(self):
        return "<SettingInstance (0x{0:x}) definition={1} container={2}>".format(id(self), self._definition, self._container)

    ## protected:
    def updateRelations(self, container):
        property_names = SettingDefinition.getPropertyNames()
        property_names.remove("value")  # Move "value" to the front of the list so we always update that first.
        property_names.insert(0, "value")

        for property_name in property_names:
            if SettingDefinition.isReadOnlyProperty(property_name):
                continue

            changed_relations = set()
            self._addRelations(changed_relations, self._definition.relations, property_name)

            # TODO: We should send this as a single change event instead of several of them.
            # That would increase performance by reducing the amount of updates.
            for relation in changed_relations:
                container.propertyChanged.emit(relation.target.key, relation.role)
                # If the value/minimum value/etc state is updated, the validation state must be re-evaluated
                if relation.role in {"value", "minimum_value", "maximum_value", "minimum_value_warning", "maximum_value_warning"}:
                    container.propertyChanged.emit(relation.target.key, "validationState")

    ##  Recursive function to put all settings that require eachother for changes of a property value in a list
    #   \param relations_set \type{set} Set of keys (strings) of settings that are influenced
    #   \param relations list of relation objects that need to be checked.
    #   \param role name of the property value of the settings
    def _addRelations(self, relations_set, relations, role):
        for relation in filter(lambda r: r.role == role, relations):
            if relation.type == SettingRelation.RelationType.RequiresTarget:
                continue
            # Do not add relation to self.
            if relation.target.key == self.definition.key:
                continue

            relations_set.add(relation)

            property_names = SettingDefinition.getPropertyNames()
            property_names.remove("value")  # Move "value" to the front of the list so we always update that first.
            property_names.insert(0, "value")
            # Ensure that all properties of related settings are added.
            for property_name in property_names:
                self._addRelations(relations_set, relation.target.relations, property_name)
