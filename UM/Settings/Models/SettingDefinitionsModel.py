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
        self._exclude = set()

        self._show_all = False

        self._visibility_handler = None

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

            containers = UM.Settings.ContainerRegistry.getInstance().findDefinitionContainers(id = self._container_id)
            if containers:
                self._container = containers[0]
            else:
                self._container = None

            self._update()

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

                self._root = definitions[0]
                self._update()

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
            self._show_all = show
            self._update()

    ##  Emitted when the showAll property changes.
    showAllChanged = pyqtSignal()

    ##  Whether or not the model should show all definitions regardless of visibility.
    @pyqtProperty(bool, fset = setShowAll, notify = showAllChanged)
    def showAll(self):
        return self._show_all

    ##  Set the list (string with keys separated by ;) to be visible
    def setVisibilityHandler(self, visibility_handler):
        if self._visibility_handler:
            self._visibility_handler.visibilityChanged.disconnect(self._onVisibilityChanged)

        self._visibility_handler = visibility_handler

        if self._visibility_handler:
            self._visibility_handler.visibilityChanged.connect(self._onVisibilityChanged)
            self._onVisibilityChanged()

    visibilityHandlerChanged = pyqtSignal()

    @pyqtProperty("QVariant", fset = setVisibilityHandler, notify = visibilityHandlerChanged)
    def visibilityHandler(self):
        return self._visibility_handler

    ##  Set the exclude property
    def setExclude(self, exclude):
        exclude = set(exclude)
        if exclude != self._exclude:
            self._exclude = exclude
            self._update()
            self.excludeChanged.emit()

    ##  Emitted whenever the exclude property changes
    excludeChanged = pyqtSignal()

    ##  This property indicates which settings should never be visibile.
    @pyqtProperty("QVariantList", fset = setExclude, notify = excludeChanged)
    def exclude(self):
        return list(self._exclude)

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

        try:
            parent_index = self._definitions.index(definition)
        except ValueError:
            return

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
            if child.children:
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

        first_child = self._getFirstVisibleChild(definition)
        if not first_child: # No visible children, mark it as collapsed and ignore the rest.
            self._expanded.remove(key)
            return

        start_index = self._definitions.index(first_child)
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
        self.setVisible(key, True)

    ##  Hide a single SettingDefinition.
    @pyqtSlot(str)
    def hide(self, key):
        self.setVisible(key, False)

    ##  Set SettingDefinition visible state in bulk
    @pyqtSlot(str, bool)
    def setVisibleBulk(self, keys, visible):
        new_visible = self._visible.copy()
        keys = keys.split(",")
        for key in keys:
            definitions = self._container.findDefinitions(key = key)
            if not definitions or definitions[0].type == "category":
                continue

            if visible and key not in new_visible:
                new_visible.add(key)
            elif not visible and key in new_visible:
                new_visible.remove(key)
        if new_visible != self._visible:
            self._visibility_handler.setVisible(new_visible)

    ##  Set a single SettingDefinition's visible state
    @pyqtSlot(str, bool)
    def setVisible(self, key, visible):
        if key in self._visible and visible:
            # Ignore already visible settings that need to be made visible.
            return

        if key not in self._visible and not visible:
            # Ignore already hidden settings that need to be hidden.
            return

        definitions = self._container.findDefinitions(key = key)
        if not definitions:
            Logger.log("e", "Tried to change visiblity of a non-existant SettingDefinition")
            return
        if visible:
            self._visible.add(key)
        else:
            self._visible.remove(key)

        # The visibility change data emit is mostly usefull if show_all is enabled, as we don't want to reset the
        # entire model at that point.
        try:
            self.dataChanged.emit(self.index(self._definitions.index(definitions[0]), 0), self.index(self._definitions.index(definitions[0]), 0), [self.VisibleRole])
        except ValueError:
            pass  # Definition was not added yet. Ignore.

        if self._visibility_handler:
            self._visibility_handler.setVisible(self._visible)

    @pyqtSlot(str, result = int)
    def getIndex(self, key):
        definitions = self._container.findDefinitions(key = key)
        if not definitions:
            return -1

        return self._definitions.index(definitions[0])

    @pyqtSlot(str, str, result = "QVariantList")
    def getRequires(self, key, role = None):
        if not self._container:
            return []

        definitions = self._container.findDefinitions(key = key)
        if not definitions:
            return []

        result = []
        for relation in definitions[0].relations:
            if relation.type is not UM.Settings.SettingRelation.RelationType.RequiresTarget:
                continue

            if role and role != relation.role:
                continue

            result.append({ "key": relation.target.key, "label": relation.target.label})

        return result

    @pyqtSlot(str, str, result = "QVariantList")
    def getRequiredBy(self, key, role = None):
        if not self._container:
            return []

        definitions = self._container.findDefinitions(key = key)
        if not definitions:
            return []

        result = []
        for relation in definitions[0].relations:
            if relation.type is not UM.Settings.SettingRelation.RelationType.RequiredByTarget:
                continue

            if role and role != relation.role:
                continue

            result.append({ "key": relation.target.key, "label": relation.target.label})

        return result

    ##  Reimplemented from QAbstractListModel
    def rowCount(self, parent = None):
        if not self._container:
            return 0

        return len(self._definitions)

    ##  Set the filter of this model based on a string.
    #   \param filter_dict Dictionary to do the filtering by.
    def setFilter(self, filter_dict):
        self._filter_dict = filter_dict
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

    settingsVisibilityChanged = pyqtSignal()

    ##  Reimplemented from QAbstractListModel
    def roleNames(self):
        return self._role_names

    ##  Get role id from a role name
    @pyqtSlot(str, result=int)
    def roleId(self, role_name):
        try:
            index = list(self._role_names.values()).index(role_name.encode())
            return list(self._role_names.keys())[index]
        except:
            pass
        return -1

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
            if child.key in self._exclude:
                continue

            if self._show_all or child.key in self._visible:
                self._definitions.append(child)
            else:
                # If a category isn't visible, this does not mean that the children can't be visible
                for item in filter(lambda i: self._show_all or i.key in self._visible, child.children):
                    self._definitions.append(item)
            if self._expanded_by_default or child.key in self._expanded:
                self.expandAll(child.key)
        self.endResetModel()
        self.settingsVisibilityChanged.emit()

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

    def _onVisibilityChanged(self):
        new_visible = self._visibility_handler.getVisible()

        self._visible = new_visible
        self.settingsVisibilityChanged.emit()

        if self._show_all:
            # We are already showing all settings, just update the visible role.
            self.dataChanged.emit(self.index(0, 0), self.index(len(self._definitions) - 1, 0))
            return

        if not self._container:
            return

        self._update()
