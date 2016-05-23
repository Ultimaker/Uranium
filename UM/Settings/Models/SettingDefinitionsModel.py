# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import collections

from PyQt5.QtCore import Qt, QAbstractListModel, QVariant, QModelIndex, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Logger import Logger
from UM.Preferences import Preferences

import UM.Settings

##  Model that provides a flattened list of the tree of SettingDefinition objects in a DefinitionContainer
#
#   This model exposes the tree of SettingDefinition objects in a DefinitionContainer as a list of settings.
#
class SettingDefinitionsModel(QAbstractListModel):
    KeyRole = Qt.UserRole + 1
    DepthRole = Qt.UserRole + 2
    VisibleRole = Qt.UserRole + 3
    ExpandedRole = Qt.UserRole + 4

    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        self._container_id = None
        self._container = None

        self._root_key = ""
        self._root = None

        self._definitions = []

        # Should everything be expanded by default?
        self._expanded_by_default = True

        self._expanded = set()
        self._visible = set()

        self._show_all = False

        Preferences.getInstance().preferenceChanged.connect(self._onPreferencesChanged)
        self._onPreferencesChanged("general/visible_settings")

        self._role_names = {
            self.KeyRole: b"key",
            self.DepthRole: b"depth",
            self.VisibleRole: b"visible",
            self.ExpandedRole: b"expanded",
        }
        index = self.ExpandedRole + 1
        for name in UM.Settings.SettingDefinition.getPropertyNames():
            self._role_names[index] = name.encode()
            index += 1

        self._filter_dict = {}

    ##  Set the containerId property.
    def setContainerId(self, container_id):
        if container_id != self._container_id:
            self._container_id = container_id

            self.beginResetModel()
            containers = UM.Settings.ContainerRegistry.getInstance().findDefinitionContainers(id = self._container_id)
            if containers:
                self._container = containers[0]
            else:
                self._container = None

            self._update()
            self.endResetModel()

            self.containerIdChanged.emit()

    ##  Emitted whenever the containerId property changes.
    containerIdChanged = pyqtSignal()
    ##  The ID of the DefinitionContainer object this model exposes.
    @pyqtProperty(str, fset = setContainerId, notify = containerIdChanged)
    def containerId(self):
        return self._container_id

    ##  Set the rootKey property.
    def setRootKey(self, key):
        if key != self._root_key:
            self._root_key = key

            if self._container:
                definitions = self._container.findDefinitions(key = key)
                if not definitions:
                    Logger.log("w", "Tried to set root of SettingDefinitionsModel to an unknown definition")
                    return

                self.beginResetModel()
                self._root = definitions[0]
                self._update()
                self.endResetModel()

            self.rootKeyChanged.emit()

    ##  Emitted when the rootKey property changes.
    rootKeyChanged = pyqtSignal()
    ##  The SettingDefinition to use as root for the list.
    @pyqtProperty(str, fset = setRootKey, notify = rootKeyChanged)
    def rootKey(self):
        return self._root_key

    ##  Set the showAll property.
    def setShowAll(self, show):
        if show != self._show_all:
            self.beginResetModel()
            self._show_all = show
            self.endResetModel()

    ##  Emitted when the showAll property changes.
    showAllChanged = pyqtSignal()
    ##  Whether or not the model should show all definitions regardless of visibility.
    @pyqtProperty(bool, fset = setShowAll, notify = showAllChanged)
    def showAll(self):
        return self._show_all

    ##  Are a specified SettingDefinitions's children visible.
    @pyqtSlot(str, result = bool)
    def isExpanded(self, key):
        return key in self._expanded

    ##  Show the children of a specified SettingDefinition.
    @pyqtSlot(str)
    def expand(self, key):
        if not self._container:
            return

        if not self._show_all and key not in self._visible:
            return

        definitions = self._container.findDefinitions(key = key)
        if not definitions:
            return

        definition = definitions[0]

        if len(definition.children) == 0:
            return
        parent_index = self._definitions.index(definition)

        start_index = parent_index + 1
        end_index = parent_index + len(definition.children)

        visible_children = []
        for child in definition.children:
            if not self._show_all and child.key not in self._visible:
                end_index -= 1
            else:
                visible_children.append(child)

        self.beginInsertRows(QModelIndex(), start_index, end_index)

        self._definitions[start_index:start_index] = visible_children

        self.endInsertRows()

        self._expanded.add(key)

    ##  Show the children of a specified SettingDefinition and all children of those settings as well.
    @pyqtSlot(str)
    def expandAll(self, key):
        if not self._container:
            return

        definitions = self._container.findDefinitions(key = key)
        if not definitions:
            return
        self.expand(key)

        for child in definitions[0].children:
            self.expandAll(child.key)

    ##  Hide the children of a specified SettingDefinition.
    @pyqtSlot(str)
    def collapse(self, key):

        if not self._container:
            return

        if key not in self._expanded:
            return

        definitions = self._container.findDefinitions(key = key)
        if not definitions:
            return

        definition = definitions[0]

        start_index = self._definitions.index(self._getFirstVisibleChild(definition))
        end_index = start_index + self._getVisibleChildCount(definition) - 1

        self.beginRemoveRows(QModelIndex(), start_index, end_index)

        for i in range((end_index - start_index) + 1):
            child_key = self._definitions[start_index].key
            if child_key in self._expanded:
                self._expanded.remove(child_key)
            del self._definitions[start_index]

        self.endRemoveRows()

        self._expanded.remove(key)

    ##  Show a single SettingDefinition.
    @pyqtSlot(str)
    def show(self, key):
        pass

    ##  Hide a single SettingDefinition.
    @pyqtSlot(str)
    def hide(self, key):
        pass

    ##  Reimplemented from QAbstractListModel
    def rowCount(self, parent = None):
        if not self._container:
            return 0

        return len(self._definitions)

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._filter_dict = filter_dict
        print("Filter dict set:", filter_dict)
        self._update()

    filterChanged = pyqtSignal()

    @pyqtProperty("QVariantMap", fset=setFilter, notify=filterChanged)
    def filter(self):
        return self._filter_dict

    ##  Reimplemented from QAbstractListModel
    def data(self, index, role):
        if not self._container:
            return QVariant()

        if not index.isValid():
            return QVariant()

        if role not in self._role_names:
            return QVariant()

        definition = self._definitions[index.row()]

        # Check if the definition matches the filter.
        # If it does not matches the filter, we can ignore it.
        matches_filter = definition.matchesFilter(**self._filter_dict)
        if not matches_filter:
            return QVariant()

        if role == self.KeyRole:
            return definition.key
        elif role == self.DepthRole:
            return self._countParents(definition)
        elif role == self.VisibleRole:
            if not self._show_all:
                return True
            else:
                return definition.key in self._visible
        elif role == self.ExpandedRole:
            return definition.key in self._expanded

        role_name = self._role_names[role]
        try:
            data = getattr(definition, role_name.decode())
        except AttributeError:
            data = ""

        if isinstance(data, collections.OrderedDict):
            result = []
            for key, value in data.items():
                result.append({"key": key, "value": value})
            return result

        return data

    ##  Reimplemented from QAbstractListModel
    def roleNames(self):
        return self._role_names

    ##  protected:

    def _update(self):
        self.beginResetModel()
        self._definitions.clear()

        if not self._container:
            return
        children_list = self._container.definitions

        if self._root:
            children_list = self._root.children

        for child in children_list:
            if self._show_all or child.key in self._visible:
                self._definitions.append(child)
                if self._expanded_by_default:
                    self.expandAll(child.key)
        self.endResetModel()

    def _countParents(self, definition):
        if definition.parent is None:
            return 0

        return 1 + self._countParents(definition.parent)

    def _getFirstVisibleChild(self, definition):
        for child in definition.children:
            if self._show_all or child.key in self._visible:
                return child

        return None

    def _getVisibleChildCount(self, definition):
        count = 0

        for child in filter(lambda i: self._show_all or i.key in self._visible, definition.children):
            count += 1
            if child.key in self._expanded:
                count += self._getVisibleChildCount(child)

        return count

    def _onPreferencesChanged(self, name):
        if name != "general/visible_settings":
            return
        new_visible = set()
        for key in Preferences.getInstance().getValue("general/visible_settings").replace("\n", ";").split(";"):
            new_visible.add(key.strip())

        if new_visible == self._visible or self._show_all:
            return

        print(new_visible)

        self.beginResetModel()
        self._visible = new_visible
        self.endResetModel()
