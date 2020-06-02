# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QAbstractListModel, QVariant, QModelIndex, pyqtSlot, pyqtProperty, pyqtSignal
from typing import Any, Callable, Dict, List


class ListModel(QAbstractListModel):
    """Convenience base class for models of a list of items.

    This class represents a list of dictionary objects that
    can be exposed to QML. It is intended primarily as a read-only
    convenience class but supports removing elements so can also be
    used for limited writing.
    """

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self._items = []  # type: List[Dict[str, Any]]
        self._role_names = {}  # type: Dict[int, bytes]

    itemsChanged = pyqtSignal()

    @pyqtProperty(int, notify = itemsChanged)
    def count(self) -> int:
        return len(self._items)

    @pyqtSlot(result = int)
    def rowCount(self, parent = None) -> int:
        """This function is necessary because it is abstract in QAbstractListModel.

        Under the hood, Qt will call this function when it needs to know how
        many items are in the model.
        This pyqtSlot will not be linked to the itemsChanged signal, so please
        use the normal count() function instead.
        """

        return self.count

    def addRoleName(self, role: int, name: str):
        # Qt roleNames expects a QByteArray. PyQt 5 does not convert str to
        # bytearray implicitly so force the conversion manually.
        self._role_names[role] = name.encode("utf-8")

    def roleNames(self):
        return self._role_names

    def data(self, index, role):
        """Reimplemented from QAbstractListModel"""

        if not index.isValid():
            return QVariant()
        return self._items[index.row()][self._role_names[role].decode("utf-8")]

    @pyqtSlot(int, result="QVariantMap")
    def getItem(self, index: int) -> Dict[str, Any]:
        """Get an item from the list"""

        try:
            return self._items[index]
        except:
            return {}

    @pyqtProperty("QVariantList", notify = itemsChanged)
    def items(self) -> List[Dict[str, Any]]:
        """The list of items in this model."""

        return self._items

    def setItems(self, items: List[Dict[str, Any]]) -> None:
        """Replace all items at once.
        :param items: The new list of items.
        """

        # We do not use model reset because of the following:
        #   - it is very slow
        #   - it can cause crashes on Mac OS X for some reason when endResetModel() is called (CURA-6015)
        # So in this case, we use insertRows(), removeRows() and dataChanged signals to do
        # smarter model update.

        old_row_count = len(self._items)
        new_row_count = len(items)
        changed_row_count = min(old_row_count, new_row_count)

        need_to_add = old_row_count < new_row_count
        need_to_remove = old_row_count > new_row_count

        # In the case of insertion and deletion, we need to call beginInsertRows()/beginRemoveRows() and
        # endInsertRows()/endRemoveRows() before we modify the items.
        # In the case of modification on the existing items, we only need to modify the items and then emit
        # dataChanged().
        #
        # Here it is simplified to replace the complete items list instead of adding/removing/modifying them one by one,
        # and it needs to make sure that the necessary signals (insert/remove/modified) are emitted before and after
        # the item replacement.

        if need_to_add:
            self.beginInsertRows(QModelIndex(), old_row_count, new_row_count - 1)
        elif need_to_remove:
            self.beginRemoveRows(QModelIndex(), new_row_count, old_row_count - 1)

        self._items = items

        if need_to_add:
            self.endInsertRows()
        elif need_to_remove:
            self.endRemoveRows()

        # Notify that the existing items have been changed.
        if changed_row_count >= 0:
            self.dataChanged.emit(self.index(0, 0), self.index(changed_row_count - 1, 0))

        # Notify with the custom signal itemsChanged to keep it backwards compatible in case something relies on it.
        self.itemsChanged.emit()

    @pyqtSlot(dict)
    def appendItem(self, item: Dict[str, Any]):
        """Add an item to the list.

        :param item: The item to add.
        """

        self.insertItem(len(self._items), item)

    @pyqtSlot(int, dict)
    def insertItem(self, index: int, item: Dict[str, Any]) -> None:
        """Insert an item into the list at an index.

        :param index: The index where to insert.
        :param item: The item to add.
        """

        self.beginInsertRows(QModelIndex(), index, index)
        self._items.insert(index, item)
        self.endInsertRows()
        self.itemsChanged.emit()

    @pyqtSlot(int)
    def removeItem(self, index: int) -> None:
        """Remove an item from the list.

        :param index: The index of the item to remove.
        """

        self.beginRemoveRows(QModelIndex(), index, index)
        del self._items[index]
        self.endRemoveRows()
        self.itemsChanged.emit()

    @pyqtSlot()
    def clear(self) -> None:
        """Clear the list."""

        self.beginResetModel()
        self._items.clear()
        self.endResetModel()
        self.itemsChanged.emit()

    @pyqtSlot(int, str, QVariant)
    def setProperty(self, index: int, property: str, value: Any) -> None:
        self._items[index][property] = value
        self.dataChanged.emit(self.index(index, 0), self.index(index, 0))

    def sort(self, fun: Callable[[Any], float]) -> None:
        """Sort the list.

        :param fun: The callable to use for determining the sort key.
        """

        self.beginResetModel()
        self._items.sort(key = fun)
        self.endResetModel()

    @pyqtSlot(str, QVariant, result = int)
    def find(self, key: str, value: Any) -> int:
        """Find a entry by key value pair

        :param key:
        :param value:
        :return: index of setting if found, None otherwise
        """

        for i in range(len(self._items)):
            if key in self._items[i]:
                if self._items[i][key] == value:
                    return i
        return -1
