from PyQt5.QtCore import QObject, QAbstractListModel, QVariant, QModelIndex, pyqtSlot, pyqtProperty

##  Convenience base class for models of a list of items.
#
#   This class represents a list of dictionary objects that
#   can be exposed to QML. It is intended primarily as a read-only
#   convenience class but supports removing elements so can also be
#   used for limited writing.
class ListModel(QAbstractListModel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._items = []

    ##  Reimplemented from QAbstractListModel
    def rowCount(self, parent):
        return len(self._items)

    ##  Reimplemented from QAbstractListModel
    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        roleNames = self.roleNames()
        return self._items[index.row()][roleNames[role]]

    ##  The list of items in this model.
    @pyqtProperty('QVariantList')
    def items(self):
        return self._items

    ##  Add an item to the list.
    @pyqtSlot(dict)
    def appendItem(self, item):
        self.insertItem(len(self._items), item)

    ##  Insert an item into the list at an index.
    #   \param index The index where to insert.
    #   \param item The item to add.
    @pyqtSlot(int, dict)
    def insertItem(self, index, item):
        self.beginInsertRows(QModelIndex(), index, index + 1)
        self._items.insert(index, item)
        self.endInsertRows()

    ##  Remove an item from the list.
    #   \param index The index of the item to remove.
    @pyqtSlot(int)
    def removeItem(self, index):
        self.beginRemoveRows(QModelIndex(), index, index + 1)
        del self._items[index]
        self.endRemoveRows()

    ##  Clear the list.
    @pyqtSlot()
    def clear(self):
        self.beginResetModel()
        self._items.clear()
        self.endResetModel()
        
    @pyqtSlot(int, str, QVariant)
    def setProperty(self, index, property, value):
        self._items[index][property] = value
        self.dataChanged.emit(self.index(index, 0), self.index(index, 0))

    ##  Sort the list.
    #   \param fun The callable to use for determining the sort key.
    def sort(self, fun):
        self._items.sort(key = fun)
