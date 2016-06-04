# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, QVariant, pyqtProperty, pyqtSlot, pyqtSignal

from UM.Logger import Logger

import UM.Settings

##  This class provides the value and change notifications for the properties of a single setting
#
#   Since setting values and other properties are provided by a stack, we need some way to
#   query the stack from QML to provide us with those values. This class takes care of that.
#
#   This class provides the property values through QObject dynamic properties so that they
#   are available from QML.
class SettingPropertyProvider(QObject):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        self._stack_id = ""
        self._stack = None
        self._key = ""
        self._watched_properties = []
        self._property_values = {}
        self._store_index = 0

    ##  Set the containerStackId property.
    def setContainerStackId(self, stack_id):
        if stack_id != self._stack_id:
            self._stack_id = stack_id

            if self._stack:
                self._stack.propertyChanged.disconnect(self._onPropertyChanged)
                self._stack.containersChanged.disconnect(self._update)

            if self._stack_id:
                stack = None
                if self._stack_id == "global":
                    self._stack = UM.Application.getInstance().getGlobalContainerStack()
                else:
                    stacks = UM.Settings.ContainerRegistry.getInstance().findContainerStacks(id = self._stack_id)
                    if stacks:
                        self._stack = stacks[0]

                if self._stack:
                    self._stack.propertyChanged.connect(self._onPropertyChanged)
                    self._stack.containersChanged.connect(self._update)
            else:
                self._stack = None

            self._update()
            self.containerStackIdChanged.emit()

    ##  Emitted when the containerStackId property changes.
    containerStackIdChanged = pyqtSignal()
    ##  The ID of the container stack we should query for property values.
    @pyqtProperty(str, fset = setContainerStackId, notify = containerStackIdChanged)
    def containerStackId(self):
        return self._stack_id

    ##  Set the watchedProperties property.
    def setWatchedProperties(self, properties):
        if properties != self._watched_properties:
            self._watched_properties = properties
            self._update()
            self.watchedPropertiesChanged.emit()

    ##  Emitted when the watchedProperties property changes.
    watchedPropertiesChanged = pyqtSignal()
    ##  A list of property names that should be watched for changes.
    @pyqtProperty("QVariantList", fset = setWatchedProperties, notify = watchedPropertiesChanged)
    def watchedProperties(self):
        return self._watched_properties

    ##  Set the key property.
    def setKey(self, key):
        if key != self._key:
            self._key = key
            self._update()
            self.keyChanged.emit()

    ##  Emitted when the key property changes.
    keyChanged = pyqtSignal()
    ##  The key of the setting that we should provide property values for.
    @pyqtProperty(str, fset = setKey, notify = keyChanged)
    def key(self):
        return self._key

    propertiesChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", notify = propertiesChanged)
    def properties(self):

        return self._property_values

    def setStoreIndex(self, index):
        if index != self._store_index:
            self._store_index = index
            self.indexChanged.emit()

    storeIndexChanged = pyqtSignal()
    @pyqtProperty(int, fset = setStoreIndex, notify = storeIndexChanged)
    def storeIndex(self):
        return self._store_index

    ##  At what level in the stack does the value for this setting occur?
    @pyqtProperty(int, notify = propertiesChanged)
    def stackLevel(self):
        for container in self._stack.getContainers():
            try:
                if container.getProperty(self._key, "value") is not None:
                    return self._stack.getContainerIndex(container)
            except AttributeError:
                continue

    ##  Set the value of a property.
    #
    #   \param stack_index At which level in the stack should this property be set?
    #   \param property_name The name of the property to set.
    #   \param property_value The value of the property to set.
    @pyqtSlot(str, "QVariant")
    def setPropertyValue(self, property_name, property_value):
        if not self._stack or not self._key:
            return

        if property_name not in self._watched_properties:
            Logger.log("w", "Tried to set a property that is not being watched")
            return

        if self._property_values[property_name] == property_value:
            return

        container = self._stack.getContainer(self._store_index)
        if isinstance(container, UM.Settings.DefinitionContainer):
            return

        container.setProperty(self._key, property_name, property_value, self._stack)

    @pyqtSlot(int)
    def removeFromContainer(self, index):
        container = self._stack.getContainer(index)
        if not container or not isinstance(container, UM.Settings.InstanceContainer):
            Logger.log("w", "Unable to remove instance from container as it was either not found or not an instance container")
            return

        container.removeInstance(self._key)

    # protected:

    def _onPropertyChanged(self, key, property_name):
        if key != self._key:
            return

        if property_name not in self._watched_properties:
            return

        value = self._getPropertyValue(property_name)


        self._property_values[property_name] = value
        self.propertiesChanged.emit()

    def _update(self, container = None):
        if not self._stack or not self._watched_properties or not self._key:
            return

        new_properties = {}
        for property_name in self._watched_properties:
            new_properties[property_name] = self._getPropertyValue(property_name)

        if new_properties != self._property_values:
            self._property_values = new_properties
            self.propertiesChanged.emit()

    def _getPropertyValue(self, property_name):
        property_value = self._stack.getProperty(self._key, property_name)
        if isinstance(property_value, UM.Settings.SettingFunction):
            property_value = property_value(self._stack)

        #if property_value is None:

        if property_name == "value":
            property_value = UM.Settings.SettingDefinition.settingValueToString(self._stack.getProperty(self._key, "type"), property_value)

        return str(property_value)
