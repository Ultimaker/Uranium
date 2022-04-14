# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List, Dict, Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, pyqtSlot, pyqtProperty


class TableModel(QAbstractTableModel):
    """ Replacement Model for qt.labs.models.TableModel which was removed from PyQT6 """

    def __init__(self, parent=None, data=[]) -> None:
        super().__init__(parent)
        self._rows = data
        self._headers = {}

    def data(self, index: QModelIndex, _: int = ...) -> Any:
        """
            Example:
                rows = [{name: "Jeff", age: 100, height: 10.2}, ....]
                headers = { 0: "name", 1: "age", 2: "height" }

                row = 0 # index of row in rows
                column = 2 # index of header in headers

                return rows[0]["height"]
        """
        if index.column() not in self._headers.keys():
            # Check if column (int) has corresponding header (str)
            return ""

        i_row = index.row()
        header = self._headers[index.column()]

        value = self._rows[i_row][header]

        return value or ""

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._rows[0]) if self._rows else 0\

    @pyqtProperty("QVariantList")
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, rows: List[Dict[str, Any]]):
        self._rows = rows

    @pyqtProperty("QVariantList")
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers: List[str]):
        """
            Stores headers and indexes as dictionary, this is used for quick lookup in data()
            headers = ["name", "age", "height"]
            self._headers = { 0: "name", 1: "age", 2: "height" }
        """
        self._headers = {i: x for i, x in enumerate(headers)}

    @pyqtSlot()
    def clear(self) -> None:
        """Clear the rows."""
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()
