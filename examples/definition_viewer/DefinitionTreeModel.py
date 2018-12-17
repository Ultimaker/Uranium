# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.ContainerRegistry import ContainerRegistry

class DefinitionTreeModel(QAbstractItemModel):
    KeyRole = Qt.UserRole + 1

    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        self._container_id = None
        self._container = None

        self._role_names = {
            self.KeyRole: b"key"
        }
        index = self.KeyRole + 1
        for name in SettingDefinition.getPropertyNames():
            self._role_names[index] = name.encode()
            index += 1

    containerIdChanged = pyqtSignal()

    def setContainerId(self, container_id):
        if container_id != self._container_id:
            self._container_id = container_id

            self.beginResetModel()
            containers = ContainerRegistry.getInstance().findDefinitionContainers(id = self._container_id)
            if containers:
                self._container = containers[0]
            else:
                self._container = None
            self.endResetModel()

            self.containerIdChanged.emit()

    @pyqtProperty(str, fset = setContainerId, notify = containerIdChanged)
    def containerId(self):
        return self._container_id

    def index(self, row, column, parent = QModelIndex()):
        if not self._container:
            return QModelIndex()

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        definition = None
        if not parent.isValid():
            definition = self._container.definitions[row]
        else:
            definition = parent.internalPointer().children[row]

        return self.createIndex(row, column, definition)

    def parent(self, child):
        if not self._container:
            return QModelIndex()

        if not child.isValid():
            return QModelIndex()

        parent = child.internalPointer().parent
        if not parent:
            return QModelIndex()

        row = None
        if not parent.parent:
            row = self._container.definitions.index(parent)
        else:
            row = parent.parent.children.index(parent)

        return self.createIndex(row, 0, parent)

    def count(self, parent = QModelIndex()):
        if not self._container:
            return 0

        if parent.column() > 0:
            return 0

        if not parent.isValid():
            return len(self._container.definitions)

        setting = parent.internalPointer()
        return len(setting.children)

    def columnCount(self, parent = QModelIndex()):
        return 1

    def data(self, index, role):
        if not self._container:
            return QVariant()

        if not index.isValid():
            return QVariant()

        if role not in self._role_names:
            return QVariant()

        role_name = self._role_names[role]
        definition = index.internalPointer()

        try:
            data = getattr(definition, role_name.decode())
        except AttributeError:
            data = ""

        return QVariant(str(data))

    def roleNames(self):
        return self._role_names

    @pyqtSlot(QModelIndex, result="QVariantMap")
    def get(self, index):
        definition = index.internalPointer()

        result = { "key": definition.key }

        for name in UM.Settings.SettingDefinition.getPropertyNames():
            try:
                result[name] = str(getattr(definition, name))
            except AttributeError:
                pass

        return result
