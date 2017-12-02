# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QQmlPropertyMap
from UM.FlameProfiler import pyqtSlot

from UM.Logger import Logger
from UM.Application import Application
from UM.Settings.SettingFunction import SettingFunction
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.SettingInstance import InstanceState
from UM.Settings.SettingRelation import RelationType
from UM.Settings.SettingDefinition import SettingDefinition

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

        self._property_map = QQmlPropertyMap(self)

        self._stack_id = ""
        self._stack = None
        self._key = ""
        self._relations = set()
        self._watched_properties = []
        self._store_index = 0
        self._value_used = None
        self._stack_levels = []
        self._remove_unused_value = True
        self._validator = None

    ##  Set the containerStackId property.
    def setContainerStackId(self, stack_id):
        if stack_id == self._stack_id:
            return # No change.

        self._stack_id = stack_id

        if self._stack:
            self._stack.propertiesChanged.disconnect(self._onPropertiesChanged)
            self._stack.containersChanged.disconnect(self._update)

        if self._stack_id:
            if self._stack_id == "global":
                self._stack = Application.getInstance().getGlobalContainerStack()
            else:
                stacks = ContainerRegistry.getInstance().findContainerStacks(id = self._stack_id)
                if stacks:
                    self._stack = stacks[0]

            if self._stack:
                self._stack.propertiesChanged.connect(self._onPropertiesChanged)
                self._stack.containersChanged.connect(self._update)
        else:
            self._stack = None

        self._validator = None
        self._update()
        self.containerStackIdChanged.emit()

    ##  Emitted when the containerStackId property changes.
    containerStackIdChanged = pyqtSignal()
    ##  The ID of the container stack we should query for property values.
    @pyqtProperty(str, fset = setContainerStackId, notify = containerStackIdChanged)
    def containerStackId(self):
        return self._stack_id

    removeUnusedValueChanged = pyqtSignal()

    def setRemoveUnusedValue(self, remove_unused_value):
        if self._remove_unused_value != remove_unused_value:
            self._remove_unused_value = remove_unused_value
            self.removeUnusedValueChanged.emit()

    @pyqtProperty(bool, fset = setRemoveUnusedValue, notify = removeUnusedValueChanged)
    def removeUnusedValue(self):
        return self._remove_unused_value

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
            self._validator = None
            self._update()
            self.keyChanged.emit()

    ##  Emitted when the key property changes.
    keyChanged = pyqtSignal()
    ##  The key of the setting that we should provide property values for.
    @pyqtProperty(str, fset = setKey, notify = keyChanged)
    def key(self):
        return self._key

    propertiesChanged = pyqtSignal()
    @pyqtProperty(QQmlPropertyMap, notify = propertiesChanged)
    def properties(self):
        return self._property_map

    @pyqtSlot()
    def forcePropertiesChanged(self):
        self._onPropertiesChanged(self._key, self._watched_properties)

    def setStoreIndex(self, index):
        if index != self._store_index:
            self._store_index = index
            self.storeIndexChanged.emit()

    storeIndexChanged = pyqtSignal()
    @pyqtProperty(int, fset = setStoreIndex, notify = storeIndexChanged)
    def storeIndex(self):
        return self._store_index

    stackLevelChanged = pyqtSignal()

    ##  At what levels in the stack does the value(s) for this setting occur?
    @pyqtProperty("QVariantList", notify = stackLevelChanged)
    def stackLevels(self):
        if not self._stack:
            return -1
        return self._stack_levels

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

        container = self._stack.getContainer(self._store_index)
        if isinstance(container, DefinitionContainer):
            return

        # In some cases we clean some stuff and the result is as when nothing as been changed manually.
        if property_name == "value" and self._remove_unused_value:
            for index in self._stack_levels:
                if index > self._store_index:
                    old_value = self.getPropertyValue(property_name, index)

                    key_state = str(self._stack.getContainer(self._store_index).getProperty(self._key, "state"))
                    # sometimes: old value is int, property_value is float
                    # (and the container is not removed, so the revert button appears)
                    if str(old_value) == str(property_value) and key_state != "InstanceState.Calculated":
                        # If we change the setting so that it would be the same as a deeper setting, we can just remove
                        # the value. Note that we only do this when this is not caused by the calculated state
                        # In this case the setting does need to be set, as it needs to be stored in the user settings.
                        self.removeFromContainer(self._store_index)
                        return
                    else:  # First value that we encountered was different, stop looking & continue as normal.
                        break

        # _remove_unused_value is used when the stack value differs from the effective value
        # i.e. there is a resolve function
        if self._property_map.value(property_name) == property_value and self._remove_unused_value:
            return

        container.setProperty(self._key, property_name, property_value)

    ##  Manually request the value of a property.
    #   The most notable difference with the properties is that you have more control over at what point in the stack
    #   you want the setting to be retrieved (instead of always taking the top one)
    #   \param property_name The name of the property to get the value from.
    #   \param stack_level the index of the container to get the value from.
    @pyqtSlot(str, int, result = "QVariant")
    def getPropertyValue(self, property_name, stack_level):
        try:
            # Because we continue to count if there are multiple linked stacks, we need to check what stack is targeted
            current_stack = self._stack
            while current_stack:
                num_containers = len(current_stack.getContainers())
                if stack_level >= num_containers:
                    stack_level -= num_containers
                    current_stack = self._stack.getNextStack()
                else:
                    break  # Found the right stack

            if not current_stack:
                Logger.log("w", "Could not find the right stack for setting %s at stack level %d while trying to get property %s", self._key, stack_level, property_name)
                return None

            value = current_stack.getContainers()[stack_level].getProperty(self._key, property_name)
        except IndexError:  # Requested stack level does not exist
            Logger.log("w", "Tried to get property of type %s from %s but it did not exist on requested index %d", property_name, self._key, stack_level)
            return None
        return value

    @pyqtSlot(int)
    def removeFromContainer(self, index):
        current_stack = self._stack
        while current_stack:
            num_containers = len(current_stack.getContainers())
            if index >= num_containers:
                index -= num_containers
                current_stack = self._stack.getNextStack()
            else:
                break  # Found the right stack

        if not current_stack:
            Logger.log("w", "Unable to remove instance from container because the right stack at stack level %d could not be found", index)
            return

        container = current_stack.getContainer(index)
        if not container or not isinstance(container, InstanceContainer):
            Logger.log("w", "Unable to remove instance from container as it was either not found or not an instance container")
            return

        container.removeInstance(self._key)

    isValueUsedChanged = pyqtSignal()
    @pyqtProperty(bool, notify = isValueUsedChanged)
    def isValueUsed(self):
        if self._value_used is not None:
            return self._value_used
        if not self._stack:
            return False
        definition = self._stack.getSettingDefinition(self._key)
        if not definition:
            return False

        relation_count = 0
        value_used_count = 0
        for key in self._relations:
            # If the setting is not a descendant of this setting, ignore it.
            if not definition.isDescendant(key):
                continue

            relation_count += 1

            if self._stack.getProperty(key, "state") != InstanceState.User:
                value_used_count += 1

            # If the setting has a formula the value is still used.
            if isinstance(self._stack.getRawProperty(key, "value"), SettingFunction):
                value_used_count += 1

        self._value_used = relation_count == 0 or (relation_count > 0 and value_used_count != 0)
        return self._value_used

    # protected:

    def _onPropertiesChanged(self, key, property_names):
        if key != self._key:
            if key in self._relations:
                self._value_used = None
                self.isValueUsedChanged.emit()
            return

        has_values_changed = False
        for property_name in property_names:
            if property_name not in self._watched_properties:
                continue

            has_values_changed = True
            self._property_map.insert(property_name, self._getPropertyValue(property_name))

        self._updateStackLevels()
        if has_values_changed:
            self.propertiesChanged.emit()

    def _update(self, container = None):
        if not self._stack or not self._watched_properties or not self._key:
            return

        self._updateStackLevels()
        relations = self._stack.getProperty(self._key, "relations")
        if relations:  # If the setting doesn't have the property relations, None is returned
            for relation in filter(lambda r: r.type == RelationType.RequiredByTarget and r.role == "value", relations):
                self._relations.add(relation.target.key)

        for property_name in self._watched_properties:
            self._property_map.insert(property_name, self._getPropertyValue(property_name))

        # Force update of value_used
        self._value_used = None
        self.isValueUsedChanged.emit()

    ##  Updates the self._stack_levels field, which indicates at which levels in
    #   the stack the property is set.
    def _updateStackLevels(self):
        levels = []
        # Start looking at the stack this provider is attached to.
        current_stack = self._stack
        index = 0
        while current_stack:
            for container in current_stack.getContainers():
                try:
                    if container.getProperty(self._key, "value") is not None:
                        levels.append(index)
                except AttributeError:
                    pass
                index += 1
            # If there is a next stack, check that one as well.
            current_stack = current_stack.getNextStack()

        if levels != self._stack_levels:
            self._stack_levels = levels
            self.stackLevelChanged.emit()

    def _getPropertyValue(self, property_name):
        property_value = self._stack.getProperty(self._key, property_name)
        if isinstance(property_value, SettingFunction):
            property_value = property_value(self._stack)

        if property_name == "value":
            setting_type =self._stack.getProperty(self._key, "type")
            if setting_type is not None:
                property_value = SettingDefinition.settingValueToString(setting_type, property_value)
            else:
                property_value = ""
        elif property_name == "validationState":
            # Setting is not validated. This can happen if there is only a setting definition.
            # We do need to validate it, because a setting defintions value can be set by a function, which could
            # be an invalid setting.
            if property_value is None:
                if not self._validator:
                    definition = self._stack.getSettingDefinition(self._key)
                    validator_type = SettingDefinition.getValidatorForType(definition.type)
                    if validator_type:
                        self._validator = validator_type(self._key)
                if self._validator:
                    property_value = self._validator(self._stack)
        return str(property_value)
