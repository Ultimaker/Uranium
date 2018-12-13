# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QAbstractListModel, QVariant, QModelIndex, pyqtSlot, pyqtProperty, pyqtSignal
from typing import Dict, List, Any



##  Convenience base class for models of a list of items.
#
#   This class represents a list of dictionary objects that
#   can be exposed to QML. It is intended primarily as a read-only
#   convenience class but supports removing elements so can also be
#   used for limited writing.
class ListModel(QAbstractListModel):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self._items = []  # type: List[Dict[str, Any]]
        self._role_names = {}  # type: Dict[int, bytes]

    itemsChanged = pyqtSignal()

    @pyqtProperty(int, notify = itemsChanged)
    def count(self) -> int:
        return len(self._items)

    ##  This function is necessary because it is abstract in QAbstractListModel.
    #
    #   Under the hood, Qt will call this function when it needs to know how
    #   many items are in the model.
    #   This pyqtSlot will not be linked to the itemsChanged signal, so please
    #   use the normal count() function instead.
    @pyqtSlot(result = int)
    def rowCount(self, parent = None) -> int:
        return self.count

    def addRoleName(self, role: int, name: str):
        # Qt roleNames expects a QByteArray. PyQt 5.5 does not convert str to bytearray implicitly so
        # force the conversion manually.
        self._role_names[role] = name.encode("utf-8")

    def roleNames(self):
        return self._role_names

    ##  Reimplemented from QAbstractListModel
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        return self._items[index.row()][self._role_names[role].decode("utf-8")]

    ##  Get an item from the list
    @pyqtSlot(int, result="QVariantMap")
    def getItem(self, index: int) -> Dict[str, Any]:
        try:
            return self._items[index]
        except:
            return {}

    ##  The list of items in this model.
    @pyqtProperty("QVariantList", notify = itemsChanged)
    def items(self) -> List[Dict[str, Any]]:
        return self._items

    ##  Replace all items at once.
    #   \param items The new list of items.
    def setItems(self, items: List[Dict[str, Any]]) -> None:
        # We do not use model reset because of the following:
        #   - it is very slow
        #   - it can cause crashes on Mac OS X for some reason when endResetModel() is called (CURA-6015)
        # So in this case, we use insertRows(), removeRows() and dataChanged signals to do
        # smarter model update.

        old_row_count = len(self._items)
        new_row_count = len(items)
        changed_row_count = min(old_row_count, new_row_count)

        for i in range(changed_row_count):
            self._items[i] = items[i]

        if old_row_count < new_row_count:
            # there are new items, append them at the end of the current item list
            self.beginInsertRows(QModelIndex(), old_row_count, new_row_count - 1)
            self._items += items[old_row_count:new_row_count]
            self.endInsertRows()

        elif old_row_count > new_row_count:
            # the number of new items is less than the current number. Remove the not-needed ones.
            self.beginRemoveRows(QModelIndex(), new_row_count, old_row_count - 1)
            self._items = self._items[:new_row_count]
            self.endRemoveRows()

        # Notify that the existing items have been changed.
        if changed_row_count >= 0:
            self.dataChanged.emit(self.index(0, 0), self.index(changed_row_count - 1, 0))

        # Notify with the custom signal itemsChanged to keep it backwards compatible in case something relies on it.
        self.itemsChanged.emit()

    ##  Add an item to the list.
    #   \param item The item to add.
    @pyqtSlot(dict)
    def appendItem(self, item: Dict[str, Any]):
        self.insertItem(len(self._items), item)

    ##  Insert an item into the list at an index.
    #   \param index The index where to insert.
    #   \param item The item to add.
    @pyqtSlot(int, dict)
    def insertItem(self, index: int, item: Dict[str, Any]) -> None:
        self.beginInsertRows(QModelIndex(), index, index)
        self._items.insert(index, item)
        self.endInsertRows()
        self.itemsChanged.emit()

    ##  Remove an item from the list.
    #   \param index The index of the item to remove.
    @pyqtSlot(int)
    def removeItem(self, index: int) -> None:
        self.beginRemoveRows(QModelIndex(), index, index)
        del self._items[index]
        self.endRemoveRows()
        self.itemsChanged.emit()

    ##  Clear the list.
    @pyqtSlot()
    def clear(self) -> None:
        self.beginResetModel()
        self._items.clear()
        self.endResetModel()
        self.itemsChanged.emit()

    @pyqtSlot(int, str, QVariant)
    def setProperty(self, index: int, property: str, value: Any) -> None:
        self._items[index][property] = value
        self.dataChanged.emit(self.index(index, 0), self.index(index, 0))

    ##  Sort the list.
    #   \param fun The callable to use for determining the sort key.
    def sort(self, fun):
        self.beginResetModel()
        self._items.sort(key = fun)
        self.endResetModel()

    ##  Find a entry by key value pair
    #   \param key
    #   \param value
    #   \return index of setting if found, None otherwise
    @pyqtSlot(str, QVariant, result = int)
    def find(self, key, value):
        for i in range(len(self._items)):
            if key in self._items[i]:
                if self._items[i][key] == value:
                    return i
        return -1
