# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Dict, Any

metadata_type = Dict[str, Any]


class SQLQueryFactory:
    """Provides the SQL query strings"""

    def __init__(self, table: str, fields: metadata_type) -> None:
        self._table = table
        self._fields = fields
        self.__create = ""
        self.__insert = ""
        self.__update = ""
        self.__select = ""
        self.__delete = ""
        self._update_queries()

    @property
    def table(self) -> str:
        """DB table name"""
        return self._table

    @table.setter
    def table(self, value: str) -> None:
        self._table = value
        self._update_queries()

    @property
    def fields(self) -> metadata_type:
        """DB fields"""
        return self._fields

    @fields.setter
    def fields(self, value: metadata_type) -> None:
        self._fields = value
        self._update_queries()

    @property
    def create(self) -> str:
        """Create SQL query """
        return self.__create

    @property
    def insert(self) -> str:
        """Insert SQL query """
        return self.__insert

    @property
    def update(self) -> str:
        """Update SQL query """
        return self.__update

    @property
    def select(self) -> str:
        """Select SQL query """
        return self.__select

    @property
    def delete(self) -> str:
        """Delete SQL query """
        return self.__delete

    def _update_queries(self) -> None:
        values = ", ".join(["?" for k in self.fields.keys()])
        columns_create = ", ".join([f"{k} {v}" for k, v in self.fields.items()])
        self.__create = f"CREATE TABLE {self.table} ({columns_create}); CREATE UNIQUE INDEX idx_{self.table}_id on {self.table} (id);"
        columns_insert = ", ".join([f"{k}" for k in self.fields.keys()])
        self.__insert = f"INSERT INTO {self.table} ({columns_insert}) VALUES ({values})"
        columns_update = ", ".join([f"{k} = ?" for k in self.fields.keys()])
        self.__update = f"UPDATE {self.table} SET {columns_update} WHERE id = ?"
        self.__select = f"SELECT * FROM {self.table} WHERE id = ?"
        self.__delete = f"DELETE FROM {self.table} WHERE id = ?"
