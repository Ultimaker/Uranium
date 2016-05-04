# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import enum

from UM.Signal import Signal, signalemitter
from UM.Logger import Logger

from . import SettingRelation
from . import Validator
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

    def setProperty(self, name, value):
        if SettingDefinition.hasProperty(name):
            if SettingDefinition.isReadOnlyProperty(name):
                Logger.log("e", "Tried to set property %s which is a read-only property", name)
                return

            if name not in self.__property_values or value != self.__property_values[name]:
                Logger.log("d", "Set property %s of instance %s", name, self)

                self.__property_values[name] = value
                if name == "value":
                    self._update()

                    self._state = InstanceState.User
                    self.stateChanged.emit(self)

                self.propertyChanged.emit(self, name)
        else:
            raise AttributeError("No property {0} defined".format(name))

    def updateProperty(self, name):
        if not SettingDefinition.hasProperty(name):
            Logger.log("e", "Trying to update unknown property %s", name)
            return

        if name == "value" and self._state == InstanceState.User:
            Logger.log("d", "Ignoring update of value for setting %s since it has been set by the user.", self._definition.key)
            return

        Logger.log("d", "Update property %s of instance %s", name, self)

        try:
            function = getattr(self._definition, name)
        except AttributeError:
            return

        result = function(self._container)

        if name not in self.__property_values or result != self.__property_values[name]:
            self.__property_values[name] = function(self._container)
            if name == "value":
                self._update()

                self._state = InstanceState.Calculated
                self.stateChanged.emit(self)

            self.propertyChanged.emit(self, name)

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
            return self._validator.getValidationState()

        return Validator.ValidatorState.Unknown

    ##  Emitted whenever this instance's validationState property changes.
    #
    #   \param instance The instance that reported the validationState change.
    validationStateChanged = Signal()

    @property
    def state(self):
        return self._state

    stateChanged = Signal()

    def __repr__(self):
        return "<SettingInstance (0x{0:x}) definition={1} container={2}>".format(id(self), self._definition, self._container)

    ## protected:

    def _update(self):
        property_names = SettingDefinition.getPropertyNames()
        property_names.remove("value")  # Move "value" to the front of the list so we always update that first.
        property_names.insert(0, "value")

        for property_name in property_names:
            if SettingDefinition.isReadOnlyProperty(property_name):
                continue

            for relation in filter(lambda r: r.role == property_name, self._definition.relations):
                if relation.type == SettingRelation.RelationType.RequiresTarget:
                    continue

                instance = self._container.getInstance(relation.target.key)
                if not instance:
                    instance = SettingInstance(relation.target, self._container)
                    self._container.addInstance(instance)

                instance.updateProperty(property_name)
