# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import collections
import os.path
from typing import List, Any, Dict, Set, Optional

from PyQt5.QtCore import Qt, QAbstractListModel, QVariant, QModelIndex, QObject, pyqtProperty, pyqtSignal

from UM.Decorators import deprecated
from UM.FlameProfiler import pyqtSlot

from UM.Logger import Logger
from UM.Settings import SettingRelation
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.Interfaces import DefinitionContainerInterface
from UM.Settings.Models.SettingPreferenceVisibilityHandler import SettingPreferenceVisibilityHandler
from UM.i18n import i18nCatalog
from UM.Application import Application

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.SettingDefinition import SettingDefinition


class SettingDefinitionsModel(QAbstractListModel):
    """Model that provides a flattened list of the tree of SettingDefinition objects in a DefinitionContainer

    This model exposes the tree of SettingDefinition objects in a DefinitionContainer as a list of settings.
    It uses two lists, one is the list of definitions which directly corresponds with the flattened contents
    of the DefinitionContainer. The other is a list matching rows in the model to indexes in the list of
    settings. This list can be quite a bit shorter than the list of definitions since all visibility criteria
    are applied.
    """

    KeyRole = Qt.UserRole + 1
    DepthRole = Qt.UserRole + 2
    VisibleRole = Qt.UserRole + 3
    ExpandedRole = Qt.UserRole + 4

    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent)

        self._container_id = None  # type: Optional[str]
        self._container = None  # type: Optional[DefinitionContainerInterface]
        self._i18n_catalog = None

        self._root_key = ""  # type: str
        self._root = None  # type: Optional[SettingDefinition]

        self._definition_list = []  # type: List[SettingDefinition]
        self._index_cache = {} # type: Dict[SettingDefinition, int]
        self._row_index_list = []  # type: List[int]

        self._expanded = set()  # type: Set[str]
        self._visible = set()  # type: Set[str]
        self._exclude = set()  # type: Set[str]

        self._show_all = False  # type: bool
        self._show_ancestors = False  # type: bool
        self._visibility_handler = None  # type: Optional[SettingPreferenceVisibilityHandler]

        self._update_visible_row_scheduled = False  # type: bool
        self._destroyed = False  # type: bool

        self._filter_dict = {}  # type: Dict[str, str]

        self._role_names = {
            self.KeyRole: b"key",
            self.DepthRole: b"depth",
            self.VisibleRole: b"visible",
            self.ExpandedRole: b"expanded",
        }  # type: Dict[int, bytes]
        index = self.ExpandedRole + 1
        for name in SettingDefinition.getPropertyNames():
            self._role_names[index] = name.encode()
            index += 1

        self.destroyed.connect(self._onDestroyed)

    showAncestorsChanged = pyqtSignal()
    """Emitted whenever the showAncestors property changes."""

    def _onDestroyed(self) -> None:
        self._destroyed = True

    @pyqtSlot(bool)
    def setDestroyed(self, value: bool) -> None:
        self._destroyed = value

    def setShowAncestors(self, show_ancestors: bool) -> None:
        if show_ancestors != self._show_ancestors:
            self._show_ancestors = show_ancestors
            self._update()
            self._scheduleUpdateVisibleRows()

    @pyqtProperty(bool, fset=setShowAncestors, notify=showAncestorsChanged)
    # Should we still show ancestors, even if filter says otherwise?
    def showAncestors(self) -> bool:
        return self._show_ancestors

    def setContainerId(self, container_id: str) -> None:
        """Set the containerId property."""

        if container_id != self._container_id:
            self._container_id = container_id

            containers = ContainerRegistry.getInstance().findDefinitionContainers(id = self._container_id)
            if containers:
                self._container = containers[0]
            else:
                self._container = None

            self._update()
            self.containerIdChanged.emit()

    containerIdChanged = pyqtSignal()
    """Emitted whenever the containerId property changes."""

    @pyqtProperty(str, fset = setContainerId, notify = containerIdChanged)
    def containerId(self) -> Optional[str]:
        """The ID of the DefinitionContainer object this model exposes."""

        return self._container_id

    def setRootKey(self, key: str) -> None:
        """Set the rootKey property."""

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

    rootKeyChanged = pyqtSignal()
    """Emitted when the rootKey property changes."""

    @pyqtProperty(str, fset = setRootKey, notify = rootKeyChanged)
    def rootKey(self) -> str:
        """The SettingDefinition to use as root for the list."""

        return self._root_key

    def setShowAll(self, show: bool) -> None:
        """Set the showAll property."""

        if show != self._show_all:
            self._show_all = show
            self.showAllChanged.emit()
            self._scheduleUpdateVisibleRows()

    showAllChanged = pyqtSignal()
    """Emitted when the showAll property changes."""

    @pyqtProperty(bool, fset = setShowAll, notify = showAllChanged)
    def showAll(self) -> bool:
        """Whether or not the model should show all definitions regardless of visibility."""

        return self._show_all

    visibilityChanged = pyqtSignal()

    def setVisibilityHandler(self, visibility_handler: SettingPreferenceVisibilityHandler) -> None:
        """Set the visibilityHandler property"""

        if self._visibility_handler:
            self._visibility_handler.visibilityChanged.disconnect(self._onVisibilityChanged)
            self._visibility_handler.visibilityChanged.disconnect(self.visibilityChanged)

        self._visibility_handler = visibility_handler

        if self._visibility_handler:
            self._visibility_handler.visibilityChanged.connect(self._onVisibilityChanged)
            self._visibility_handler.visibilityChanged.connect(self.visibilityChanged)
            self._onVisibilityChanged()

        self.visibilityHandlerChanged.emit()
        self._onVisibilityChanged()

    visibilityHandlerChanged = pyqtSignal()
    """Emitted whenever the visibilityHandler property changes"""
    @pyqtProperty("QVariant", fset = setVisibilityHandler, notify = visibilityHandlerChanged)
    def visibilityHandler(self):
        """An instance of SettingVisibilityHandler to use to determine which settings should be visible."""

        return self._visibility_handler

    def setExclude(self, exclude: Set[str]) -> None:
        """Set the exclude property"""

        exclude = set(exclude)
        if exclude != self._exclude:
            self._exclude = exclude
            self.excludeChanged.emit()
            self._scheduleUpdateVisibleRows()

    excludeChanged = pyqtSignal()
    """Emitted whenever the exclude property changes"""

    @pyqtProperty("QVariantList", fset = setExclude, notify = excludeChanged)
    def exclude(self):
        """This property indicates which settings should never be visibile."""

        return list(self._exclude)

    def setExpanded(self, expanded: List[str]) -> None:
        """Set the expanded property"""
        new_expanded = set()

        categories_list = []
        for definition in self._definition_list:
            if definition.type == "category":
                categories_list.append(definition.key)
        for item in expanded:
            if item == "*":
                for definition in self._definition_list:
                    if definition.children:
                        new_expanded.add(definition.key)
            else:
                new_expanded.add(str(item))
                if item in categories_list:
                    new_expanded.update(self._expandRecursive(item))

        if new_expanded != self._expanded:
            self._expanded = new_expanded
            self.expandedChanged.emit()
            self._scheduleUpdateVisibleRows()
        self._scheduleUpdateVisibleRows()

    expandedChanged = pyqtSignal()
    """Emitted whenever the expanded property changes"""

    @pyqtProperty("QStringList", fset = setExpanded, notify = expandedChanged)
    def expanded(self) -> List[str]:
        """This property indicates which settings should never be visibile."""

        return list(self._expanded)

    visibleCountChanged = pyqtSignal()

    @pyqtProperty(int, notify = visibleCountChanged)
    def visibleCount(self) -> int:
        count = 0
        for index in self._row_index_list:
            definition = self._definition_list[index]
            if definition.key in self._visible:
                count += 1

        return count

    @pyqtProperty(int, notify = visibleCountChanged)
    def categoryCount(self) -> int:
        count = 0
        for index in self._row_index_list:
            definition = self._definition_list[index]
            if definition.type == "category":
                count += 1

        return count

    def setFilter(self, filter_dict: Dict[str, str]) -> None:
        """Set the filter of this model based on a string.

        :param filter_dict: Dictionary to do the filtering by.
        """

        if filter_dict != self._filter_dict:
            self._filter_dict = filter_dict
            self.filterChanged.emit()
            self._scheduleUpdateVisibleRows()

    filterChanged = pyqtSignal()

    @pyqtProperty("QVariantMap", fset=setFilter, notify=filterChanged)
    def filter(self):
        return self._filter_dict

    @pyqtSlot(str)
    def expand(self, key: str) -> None:
        """Show the children of a specified SettingDefinition."""

        if key not in self._expanded:
            self._expanded.add(key)
            self.expandedChanged.emit()
            self._scheduleUpdateVisibleRows()

    def _getDefinitionsByKey(self, key: str) -> List["SettingDefinition"]:
        if not self._container:
            return []

        return self._container.findDefinitions(key = key)

    def _expandRecursive(self, key: str) -> Set[str]:
        definitions = self._getDefinitionsByKey(key)
        if not definitions:
            return set()

        expanded_settings = {key}
        for child in definitions[0].children:
            expanded_settings.update(self._expandRecursive(child.key))

        return expanded_settings

    @pyqtSlot(str)
    def expandRecursive(self, key: str, *, emit_signal: bool = True ) -> None:
        """
        Show the children of a specified SettingDefinition and all children of those settings as well.

        :param key: Key of the setting to expand
        :param emit_signal: Should signals be emitted when expanding. Can only be set as keyword argument.
        :return:
        """

        definitions = self._getDefinitionsByKey(key)
        if not definitions:
            return

        self._expanded.add(key)

        for child in definitions[0].children:
            self.expandRecursive(child.key, emit_signal = False)

        if emit_signal:
            self.expandedChanged.emit()
            self._scheduleUpdateVisibleRows()

    #@deprecated("Use collapseRecursive instead.", "4.5")  # Commented out because these two decorators don't work together.
    @pyqtSlot(str)
    def collapse(self, key: str) -> None:
        return self.collapseRecursive(key)

    @pyqtSlot(str)
    def collapseRecursive(self, key: str, *, emit_signal: bool = True) -> None:
        """
        Hide the children of a specified SettingDefinition and all children of those settings as well.

        :param key: Key of the setting to collapse
        :param emit_signal: Should signals be emitted when collapsing. Can only be set as keyword argument.
        :return:
        """

        definitions = self._getDefinitionsByKey(key)
        if not definitions:
            return

        if key not in self._expanded:
            return

        self._expanded.remove(key)

        for child in definitions[0].children:
            self.collapseRecursive(child.key, emit_signal = False)

        if emit_signal:
            self.expandedChanged.emit()
            self._scheduleUpdateVisibleRows()

    @pyqtSlot()
    def collapseAllCategories(self) -> None:
        self.setExpanded([])

    @pyqtSlot(str)
    def show(self, key: str) -> None:
        """Show a single SettingDefinition."""

        self.setVisible(key, True)

    @pyqtSlot(str)
    def hide(self, key: str) -> None:
        """Hide a single SettingDefinition."""

        self.setVisible(key, False)

    @pyqtSlot(bool)
    def setAllExpandedVisible(self, visible: bool) -> None:
        new_visible = set()

        for index in self._row_index_list:
            definition = self._definition_list[index]
            if definition.type != "category":
                new_visible.add(self._definition_list[index].key)

        if self._visibility_handler:
            if visible:
                self._visibility_handler.setVisible(new_visible | self._visible)
            else:
                self._visibility_handler.setVisible(self._visible - new_visible)

    @pyqtSlot(bool)
    def setAllVisible(self, visible: bool) -> None:
        new_visible = set()

        for definition in self._definition_list:
            if definition.type != "category":
                new_visible.add(definition.key)

        if self._visibility_handler:
            if visible:
                self._visibility_handler.setVisible(new_visible | self._visible)
            else:
                self._visibility_handler.setVisible(self._visible - new_visible)

    @pyqtSlot(str, bool)
    def setVisible(self, key: str, visible: bool) -> None:
        """Set a single SettingDefinition's visible state"""

        if key in self._visible and visible:
            # Ignore already visible settings that need to be made visible.
            return

        if key not in self._visible and not visible:
            # Ignore already hidden settings that need to be hidden.
            return

        definitions = self._getDefinitionsByKey(key)
        if not definitions:
            Logger.log("e", "Tried to change visibility of a non-existent SettingDefinition")
            return

        if visible:
            self._visible.add(key)
        else:
            self._visible.remove(key)

        if self._visibility_handler:
            self._visibility_handler.setVisible(self._visible)

    @pyqtSlot(str, result = bool)
    def getVisible(self, key: str) -> bool:
        """Get a single SettingDefinition's visible state"""

        return key in self._visible

    @pyqtSlot(str, result = int)
    def getIndex(self, key: str) -> int:
        definitions = self._getDefinitionsByKey(key)
        if not definitions:
            return -1

        index = self._definition_list.index(definitions[0])

        # Make sure self._row_index_list is populated
        if self._update_visible_row_scheduled:
            self._update_visible_row_scheduled = False
            self._updateVisibleRows()

        try:
            return self._row_index_list.index(index)
        except ValueError:
            return -1

    @pyqtSlot(str, str, result = "QVariantList")
    def getRequires(self, key: str, role: str = None) -> List[Dict[str, Any]]:
        definitions = self._getDefinitionsByKey(key)
        if not definitions:
            return []

        result = []
        for relation in definitions[0].relations:
            if relation.type is not SettingRelation.RelationType.RequiresTarget:
                continue

            if role and role != relation.role:
                continue

            label = relation.target.label
            if self._i18n_catalog:
                label = self._i18n_catalog.i18nc(relation.target.key + " label", label)

            result.append({ "key": relation.target.key, "label": label})

        return result

    @pyqtSlot(str, str, result = "QVariantList")
    def getRequiredBy(self, key: str, role: str = None) -> List[Dict[str, Any]]:
        definitions = self._getDefinitionsByKey(key)
        if not definitions:
            return []

        result = []
        for relation in definitions[0].relations:
            if relation.type is not SettingRelation.RelationType.RequiredByTarget:
                continue

            if role and role != relation.role:
                continue

            label = relation.target.label
            if self._i18n_catalog:
                label = self._i18n_catalog.i18nc(relation.target.key + " label", label)

            result.append({ "key": relation.target.key, "label": label})

        return result

    itemsChanged = pyqtSignal()
    """Reimplemented from ListModel only because we want to use it in static
    context in the subclass."""

    @pyqtProperty(int, notify = itemsChanged)
    def count(self) -> int:
        """Reimplemented from QAbstractListModel

        Note that count() is overridden from QAbstractItemModel. The signature
        of the method in that class is "int count()" which makes this slot
        declaration incorrect.
        TODO: fix the pointer when actually using this parameter.
        """

        if not self._container:
            return 0

        return len(self._row_index_list)

    @pyqtSlot(QObject, result = int)
    def rowCount(self, parent = None) -> int:
        """This function is necessary because it is abstract in QAbstractListModel.

        Under the hood, Qt will call this function when it needs to know how many items are in the model.
        This pyqtSlot will not be linked to the itemsChanged signal, so please use the normal count() function instead.
        """

        return self.count

    def data(self, index, role):
        """Reimplemented from QAbstractListModel"""

        if not self._container:
            return QVariant()

        if not index.isValid():
            return QVariant()

        if role not in self._role_names:
            return QVariant()

        try:
            definition = self._definition_list[self._row_index_list[index.row()]]
        except IndexError:
            # Definition is not visible or completely not in the list
            return QVariant()

        if role == self.KeyRole:
            return definition.key
        elif role == self.DepthRole:
            return len(definition.getAncestors())
        elif role == self.VisibleRole:
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
                if self._i18n_catalog:
                    value = self._i18n_catalog.i18nc(definition.key + " option " + key, value)

                result.append({"key": key, "value": value})
            return result

        if isinstance(data, str) and self._i18n_catalog:
            data = self._i18n_catalog.i18nc(definition.key + " " + role_name.decode(), data)

        return data

    def roleNames(self) -> Dict[int, bytes]:
        """Reimplemented from QAbstractListModel"""

        return self._role_names

    def _onVisibilityChanged(self) -> None:
        if self._visibility_handler:
            self._visible = self._visibility_handler.getVisible()

        if self._show_all:
            # We only need to emit the data in the case of the show all, otherwise the
            # data will be filtered anyway.
            # it should be possible (and faster) to emit a single datachanged, but this
            # caused problems with the settingVisibilityPreference panel.
            # I couldn't figure that out, so perhaps it's worht it to re-evaluate this later
            for row in range(len(self._row_index_list)):
                self.dataChanged.emit(self.index(row, 0), self.index(row, 0), [self.VisibleRole])

        self._updateVisibleRows()

    # Schedules to call _updateVisibleRows() later.
    def _scheduleUpdateVisibleRows(self) -> None:
        if not self._update_visible_row_scheduled:
            self._update_visible_row_scheduled = True
            Application.getInstance().callLater(self._updateVisibleRows)

    @pyqtSlot()
    def forceUpdate(self) -> None:
        """Force updating the model."""

        self._update()

    # Update the internal list of definitions and the visibility mapping.
    #
    # Note that this triggers a model reset and should only be called when the
    # underlying data needs to be updated. Otherwise call _updateVisibleRows.
    def _update(self) -> None:
        if not self._container:
            return

        # Try and find a translation catalog for the definition
        for file_name in self._container.getInheritedFiles():
            catalog = i18nCatalog(os.path.basename(file_name))
            if catalog.hasTranslationLoaded():
                self._i18n_catalog = catalog

        if self._root:
            new_definitions = self._root.findDefinitions()
        else:
            new_definitions = self._container.findDefinitions()

        # Check if a full reset is required
        if len(new_definitions) != len(self._definition_list):
            self.beginResetModel()
            self._definition_list = new_definitions
            self._updateIndexCache()
            self._row_index_list.clear()
            self._scheduleUpdateVisibleRows()
            self.endResetModel()
        else:
            # If the length hasn't changed, we can just notify that the data was changed. This will prevent the existing
            # QML setting items from being re-created every you switch between machines.
            self._definition_list = new_definitions
            self._updateIndexCache()
            self._scheduleUpdateVisibleRows()
            self.dataChanged.emit(self.index(0, 0), self.index(len(self._definition_list) - 1, 0))

    def _updateIndexCache(self) -> None:
        # During updating the visible rows, we need to do a lot of index operations. Those are rather expensive, so
        # we create a cache here. That way we we can get the index in constant time!
        self._index_cache = {definition: index for index, definition in enumerate(self._definition_list)}

    # Update the list of visible rows.
    #
    # This will compute the difference between the old state and the new state and
    # insert/remove rows as appropriate.
    def _updateVisibleRows(self) -> None:
        # This function is scheduled on the Qt event loop. By the time this is called, this object can already been
        # destroyed because the owner QML widget was destroyed or so. We cannot cancel a call that has been scheduled,
        # so in this case, we should do nothing if this object has already been destroyed.
        if self._destroyed:
            return

        # Reset the scheduled flag
        self._update_visible_row_scheduled = False

        currently_visible = set(self._row_index_list) # A set of currently visible items

        new_visible = set() # A new set of visible items
        for index in range(len(self._definition_list)):
            if self._isDefinitionVisible(self._definition_list[index]):
                new_visible.add(index)

        # Calculate the difference between the sets. The items that are in new_visible and
        # not in currently_visible are items that need to be added, the items that are in
        # currently_visible and not in new_visible are items that should be removed.
        to_add = new_visible - currently_visible
        to_remove = currently_visible - new_visible

        # Add the new items. Currently doing this one by one since that proved fast enough.
        for index in sorted(list(to_add)):
            row = self._findRowToInsert(index)
            self.beginInsertRows(QModelIndex(), row, row)
            self._row_index_list.insert(row, index)
            self.endInsertRows()

        # Remove items. Also doing this one by one currently.
        for index in sorted(list(to_remove)):
            row = self._row_index_list.index(index)
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._row_index_list[row]
            self.endRemoveRows()

        self.visibleCountChanged.emit()

    # Helper function to determine if a setting(row) should be visible or not.
    def _isDefinitionVisible(self, definition: SettingDefinition, **kwargs: Any) -> bool:
        key = definition.key

        # If it is in the list of things to exclude it is never going to be visible.
        if key in self._exclude:
            return False

        # If any of its ancestors is in the list of things to exclude it also should never be visible.
        if definition.getAncestors() & self._exclude:
            return False

        # If its parent is not expanded we should not show the setting.
        if definition.parent and not definition.parent.key in self._expanded:
            return False

        # If it is not marked as visible we do not have to show it.
        if not self._show_all and key not in self._visible:
            return False

        # If it does not match the current filter, it should not be shown.
        filter = self._filter_dict.copy()
        filter["i18n_catalog"] = self._i18n_catalog

        if self._filter_dict and not definition.matchesFilter(**filter):
            if self._show_ancestors:
                if self._isAnyDescendantFiltered(definition):
                    return True
            return False

        # We should not show categories that are empty
        if definition.type == "category":
            if not self._isAnyDescendantVisible(definition):
                return False

        return True

    def _isAnyDescendantFiltered(self, definition: SettingDefinition) -> bool:
        filter = self._filter_dict.copy()
        filter["i18n_catalog"] = self._i18n_catalog
        for child in definition.children:
            if self._isAnyDescendantFiltered(child):
                return True
            if self._filter_dict and child.matchesFilter(**filter):
                return True
        return False

    # Determines if any child of a definition is visible.
    def _isAnyDescendantVisible(self, definition: SettingDefinition) -> bool:
        if not self._container:
            return False
        if self._show_all:
            return True

        filter = self._filter_dict.copy()
        filter["i18n_catalog"] = self._i18n_catalog
        for child in definition.children:
            if child.key in self._exclude:
                continue

            if self._filter_dict and not child.matchesFilter(**filter):
                continue

            if child.key in self._visible:
                if self._container.getProperty(child.key, "enabled"):
                    return True

            if self._isAnyDescendantVisible(child):
                return True

        return False

    # Find the row where we should insert a certain index.
    def _findRowToInsert(self, index: int) -> int:
        parent = self._definition_list[index].parent
        parent_row = 0
        while parent:
            parent_index = self._index_cache[parent]
            try:
                parent_row = self._row_index_list.index(parent_index)
                break
            except ValueError:
                parent = parent.parent

        insert_row = parent_row

        # Since indexes are by definition ordered, we can greatly simplify this bit since we can just assume
        # any setting with an index < the index to insert should come before this index.
        while insert_row < len(self._row_index_list) and self._row_index_list[insert_row] < index:
            insert_row += 1

        return insert_row
