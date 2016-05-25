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
    Logger.log("d", "Set property {0} of instance {1} to value {2}, updating using values from {3}".format(property_name, instance, property_value, container))

def _traceUpdateProperty(instance, property_name, container):
    Logger.log("d", "Updating property {0} of instance {1} using container {2}".format(property_name, instance, container))

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
            self._validator = validator_type(self)

        self._state = InstanceState.Default

        self.__property_values = {}

    def __getattr__(self, name):
        if name in self.__property_values:
            value = self.__property_values[name]
            if isinstance(value, str):
                return SettingDefinition.settingValueFromString(self._definition.type, value)
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

                self.__property_values[name] = value
                if name == "value":
                    if not container:
                        container = self._container

                    self._state = InstanceState.User
                    self.propertyChanged.emit(self, "state")

                    self._update(container)

                if self._validator:
                    self._validator.validate()
                    self.propertyChanged.emit(self, "validationState")

                self.propertyChanged.emit(self, name)
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


        try:
            function = getattr(self._definition, name)
        except AttributeError:
            return

        if not container:
            container = self._container

        result = function(container)
        self.__property_values[name] = result
        if name == "value":
            self._update(container)

            self._state = InstanceState.Calculated
            self.propertyChanged.emit(self, "state")

        if self._validator:
            self._validator.validate()
            self.propertyChanged.emit(self, "validationState")

        self.propertyChanged.emit(self, name)

    def recalculate(self, container):
        self._update(container)

        if self._validator:
            self._validator.validate()
            self.propertyChanged.emit(self, "validationState")

    ##  Emitted whenever a property of this instance changes.
    #
    #   \param instance The instance that reported the property change (usually self).
    #   \param property The name of the property that changed.
    propertyChanged = Signal()

    ##  The SettingDefintion this instance maintains state for.
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
            return self._validator.state

        return Validator.ValidatorState.Unknown

    @property
    def state(self):
        return self._state

    def __repr__(self):
        return "<SettingInstance (0x{0:x}) definition={1} container={2}>".format(id(self), self._definition, self._container)

    ## protected:

    def _update(self, container):
        property_names = SettingDefinition.getPropertyNames()
        property_names.remove("value")  # Move "value" to the front of the list so we always update that first.
        property_names.insert(0, "value")

        for property_name in property_names:
            if SettingDefinition.isReadOnlyProperty(property_name):
                continue

            if isinstance(getattr(self._definition, property_name), SettingFunction.SettingFunction) and not property_name in self.__property_values:
                self.updateProperty(property_name, container)

            for relation in filter(lambda r: r.role == property_name, self._definition.relations):
                if relation.type == SettingRelation.RelationType.RequiresTarget:
                    continue

                instance = self._container.getInstance(relation.target.key)
                if not instance:
                    instance = SettingInstance(relation.target, self._container)
                    self._container.addInstance(instance)

                instance.updateProperty(property_name, container)
