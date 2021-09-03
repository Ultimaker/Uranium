from typing import Dict, Any

from .SQLFilter import SQLFilter
from .SQLQuery import SQLQuery

metadata_type = Dict[str, Any]


class SQLQueryFactory:
    """Provides the SQL query strings"""

    def __init__(self, table: str, fields: metadata_type) -> None:
        self._table = table
        self._fields = fields
        self._update_queries()
        self.create = SQLFilter("CREATE TABLE {table} (id text, {fields}); CREATE UNIQUE INDEX idx_{table}_id on {table} (id);")
        self.insert = SQLFilter("INSERT INTO {table} (id, {columns}) VALUES (?, {values})")
        self.update = SQLFilter("UPDATE {table} SET {columns}", where = "id = ?")
        self.select = SQLFilter("SELECT {columns} FROM {table}", where = "id = ?")
        self.delete = SQLFilter("DELETE FROM {table}", where = "id = ?")

    create = SQLQuery()
    # SQL create string, can be dynamically modified by specifying: table (table_name), fields (field_name field_type, ...)

    insert = SQLQuery()
    # SQL insert string, can be dynamically modified by specifying: table (table_name), columns (field_name, ...), values (?, ...)

    update = SQLQuery()
    # SQL update string, can be dynamically modified by specifying: table (table_name), columns (field_name = ?, ...), where (field_name = ?, ...)

    select = SQLQuery()
    # SQL select string, can be dynamically modified by specifying: table (table_name), columns (field_name, ...), where (field_name = ?, ...)

    delete = SQLQuery()
    # SQL delete string, can be dynamically modified by specifying: table (table_name), where (field_name = ?, ...)

    @property
    def table(self) -> str:
        """DB table name"""
        return self._table

    @table.setter
    def table(self, value: str) -> None:
        self._table = value

    @property
    def fields(self) -> metadata_type:
        """DB fields"""
        return self._fields

    @fields.setter
    def fields(self, value: metadata_type) -> None:
        self._fields = value
        self._update_queries()

    def _update_queries(self) -> None:
        """
        Each SQLQuery where the queries can be dynamically overwritten need to have a private
        attribute for there default values, these need to be named according to self._<name>_<overload_attribute>
        """
        self._create_fields = ", ".join([f"{k} {v}" for k, v in self._fields.items()])
        self._insert_values = ", ".join(["?" for k in self._fields.keys()])
        self._insert_columns = ", ".join([f"{k}" for k in self._fields.keys()])
        self._select_columns = "*"
        self._update_columns = ", ".join([f"{k} = ?" for k in self._fields.keys()])
