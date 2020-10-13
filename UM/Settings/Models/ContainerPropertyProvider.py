# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, QVariant, pyqtProperty, pyqtSignal
from UM.FlameProfiler import pyqtSlot
from UM.Logger import Logger

from UM.Settings.SettingFunction import SettingFunction
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer


class ContainerPropertyProvider(QObject):
    """This class provides the value and change notifications for the properties of a single setting

    This class provides the property values through QObject dynamic properties so that they
    are available from QML.
    """

    def __init__(self, parent = None):
        super().__init__(parent = parent)

        self._container_id = ""
        self._container = None
        self._key = ""
        self._watched_properties = []
        self._property_values = {}

    def setContainerId(self, container_id):
        """Set the containerId property."""

        if container_id == self._container_id:
            return # No change.

        self._container_id = container_id

        if self._container:
            self._container.propertyChanged.disconnect(self._onPropertyChanged)

        if self._container_id:
            containers = ContainerRegistry.getInstance().findContainers(id = self._container_id)
            if containers:
                self._container = containers[0]

            if self._container:
                self._container.propertyChanged.connect(self._onPropertyChanged)
        else:
            self._container = None

        self._update()
        self.containerIdChanged.emit()

    containerIdChanged = pyqtSignal()
    """Emitted when the containerId property changes."""
    @pyqtProperty(str, fset = setContainerId, notify = containerIdChanged)
    def containerId(self):
        """The ID of the container we should query for property values."""

        return self._container_id

    def setWatchedProperties(self, properties):
        """Set the watchedProperties property."""

        if properties != self._watched_properties:
            self._watched_properties = properties
            self._update()
            self.watchedPropertiesChanged.emit()

    watchedPropertiesChanged = pyqtSignal()
    """Emitted when the watchedProperties property changes."""

    @pyqtProperty("QVariantList", fset = setWatchedProperties, notify = watchedPropertiesChanged)
    def watchedProperties(self):
        """A list of property names that should be watched for changes."""

        return self._watched_properties

    def setKey(self, key):
        """Set the key property."""

        if key != self._key:
            self._key = key
            self._update()
            self.keyChanged.emit()

    keyChanged = pyqtSignal()
    """Emitted when the key property changes."""

    @pyqtProperty(str, fset = setKey, notify = keyChanged)
    def key(self):
        """The key of the setting that we should provide property values for."""

        return self._key

    propertiesChanged = pyqtSignal()

    @pyqtProperty("QVariantMap", notify = propertiesChanged)
    def properties(self):
        return self._property_values

    @pyqtSlot(str, "QVariant")
    def setPropertyValue(self, property_name, property_value):
        """Set the value of a property.

        :param property_name: The name of the property to set.
        :param property_value: The value of the property to set.
        """

        if not self._container or not self._key:
            return

        if ContainerRegistry.getInstance().isReadOnly(self._container_id):
            return

        if property_name not in self._watched_properties:
            Logger.log("w", "Tried to set a property that is not being watched")
            return

        if self._property_values[property_name] == property_value:
            return

        if isinstance(self._container, DefinitionContainer):
            return

        self._container.setProperty(self._key, property_name, property_value)

    # protected:

    def _onPropertyChanged(self, key, property_name):
        if key != self._key:
            return

        if property_name not in self._watched_properties:
            return
        value = self._getPropertyValue(property_name)

        if self._property_values.get(property_name, None) != value:
            self._property_values[property_name] = value
            self.propertiesChanged.emit()

    def _update(self, container = None):
        if not self._container or not self._watched_properties or not self._key:
            return

        new_properties = {}
        for property_name in self._watched_properties:
            new_properties[property_name] = self._getPropertyValue(property_name)

        if new_properties != self._property_values:
            self._property_values = new_properties
            self.propertiesChanged.emit()

    def _getPropertyValue(self, property_name: str) -> str:
        property_value = self._container.getProperty(self._key, property_name)
        if isinstance(property_value, SettingFunction):
            property_value = property_value(self._container)

        if property_name == "value":
            setting_type = self._container.getProperty(self._key, "type")
            if not setting_type:
                instance = self._container.getInstance(self._key)
                if instance:
                    setting_type = instance.definition.type

            if setting_type:
                property_value = SettingDefinition.settingValueToString(setting_type, property_value)

        return str(property_value)
