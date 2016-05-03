# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter
from UM.Logger import Logger

from . import SettingRelation
from . import Validator

##  Encapsulates all state of a setting.
#
#
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

        self.__property_values = {}

    def __getattr__(self, name):
        if name in self.__property_values:
            return self.__property_values[name]

        raise AttributeError("'SettingInstance' object has no attribute '{0}'".format(name))

    def setProperty(self, name, value):
        if self._definition.hasProperty(name):
            if self._definition.isReadOnlyProperty(name):
                Logger.log("e", "Tried to set property %s which is a read-only property", name)
                return

            if name not in self.__property_values or value != self.__property_values[name]:
                Logger.log("d", "Set property %s of instance %s", name, self)

                self.__property_values[name] = value
                if name == "value":
                    self._update()

                self.propertyChanged.emit(self, name)
        else:
            raise AttributeError("No property {0} defined".format(name))

    def updateProperty(self, name):
        if not self._definition.hasProperty(name):
            Logger.log("e", "Trying to update unknown property %s", name)
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



    def __repr__(self):
        return "<SettingInstance (0x{0:x}) definition={1} container={2}>".format(id(self), self._definition, self._container)

    ## protected:

    def _update(self):
        property_names = self._definition.getPropertyNames()
        property_names.remove("value") # Move "value" to the front of the list so we always update that first.
        property_names.insert(0, "value")

        for property_name in property_names:
            if self._definition.isReadOnlyProperty(property_name):
                continue

            for relation in filter(lambda r: r.role == property_name, self._definition.relations):
                if relation.type == SettingRelation.RelationType.RequiresTarget:
                    continue

                instance = self._container.getInstance(relation.target.key)
                if not instance:
                    instance = SettingInstance(relation.target, self._container)
                    self._container.addInstance(instance)

                instance.updateProperty(property_name)
