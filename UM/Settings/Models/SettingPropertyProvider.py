# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, QVariant, pyqtProperty, pyqtSlot, pyqtSignal

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

    ##  Set the containerStackId property.
    def setContainerStackId(self, stack_id):
        if stack_id != self._stack_id:
            self._stack_id = stack_id

            if self._stack:
                self._stack.propertyChanged.disconnect(self._onPropertyChanged)

            if self._stack_id:
                stacks = UM.Settings.ContainerRegistry.getInstance().findContainerStacks(id = self._stack_id)
                if not stacks:
                    self._stack = None
                else:
                    self._stack = stacks[0]
                    self._stack.propertyChanged.connect(self._onPropertyChanged)
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

    ##  Set the value of a property.
    #
    #   \param stack_index At which level in the stack should this property be set?
    #   \param property_name The name of the property to set.
    #   \param property_value The value of the property to set.
    @pyqtSlot(int, str, "QVariant")
    def setPropertyValue(self, stack_index, property_name, property_value):
        if not self._stack or not self._key:
            return

        container = self._stack.getContainer(stack_index)
        container.setProperty(self._key, property_name, property_value)

    # protected:

    def _onPropertyChanged(self, key, property_name):
        if key != self._key:
            return

        if property_name not in self._watched_properties:
            return

        self.setProperty(property_name, self._stack.getPropertyValue(property_name))

    def _update(self):
        #if not self._stack or not self._watched_properties or not self._key:
            #return

        dynamic_property_names = self.dynamicPropertyNames()

        for property_name in self._watched_properties:
            try:
                index = dynamic_property_names.index(property_name)
                del dynamic_property_names[index]
            except ValueError:
                pass

            self.setProperty(property_name, "unknown")

            print(self.property(property_name))

            #value = self._stack.getProperty(self._key, property_name)
            #if value:
                #self.setProperty(property_name, value)
            #else:
                #self.setProperty(property_name, "unknown")

        #for name in dynamic_property_names:
            #self.setProperty(name, QVariant())
