from typing import Dict, Any

from .SQLFilter import SQLFilter

metadata_type = Dict[str, Any]


class SQLQueryFactory:
    """Provides the SQL query strings"""

    def __init__(self, table: str, fields: metadata_type) -> None:
        self._table = table
        self._fields = fields
        self.__create = ""
        self.__insert = ""
        self.__update = ""
        self.__select = SQLFilter("")
        self.__select_all = SQLFilter("")
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
    def select(self) -> SQLFilter:
        """Select SQL query """
        return self.__select

    @property
    def select_all(self) -> SQLFilter:
        """Select all rows SQL query """
        return self.__select_all

    @property
    def delete(self) -> str:
        """Delete SQL query """
        return self.__delete

    def _update_queries(self) -> None:
        columns_create = ", ".join([f"{k} {v}" for k, v in self.fields.items()])
        self.__create = f"CREATE TABLE {self.table} (id text, {columns_create}); CREATE UNIQUE INDEX idx_{self.table}_id on {self.table} (id);"
        columns_insert = ", ".join([f"{k}" for k in self.fields.keys()])
        values = ", ".join(["?" for k in self.fields.keys()])
        self.__insert = f"INSERT INTO {self.table} (id, {columns_insert}) VALUES (?, {values})"
        columns_update = ", ".join([f"{k} = ?" for k in self.fields.keys()])
        self.__update = f"UPDATE {self.table} SET {columns_update} WHERE id = ?"
        self.__select = SQLFilter(f"SELECT {{}} FROM {self.table} WHERE id = ?")
        self.__select_all = SQLFilter(f"SELECT {{}} FROM {self.table}")
        self.__delete = f"DELETE FROM {self.table} WHERE id = ?"
