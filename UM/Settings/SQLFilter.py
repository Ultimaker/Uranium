from typing import Union, Iterable
from collections import UserString

class SQLFilter(UserString):
    """Create a SQL query string which allows to input field specifications

    Usage:
        sql_filter = SQLFilter(f"SELECT {{}} FROM table_name WHERE id = ?")
        cursor.execute(sql_filter)  # Will execute: SELECT * FROM table_name WHERE id = ?
        cursor.execute(sql_filter["id", "name"])  # Will execute: SELECT id, name FROM table_name WHERE id = ?
    """
    def __getitem__(self, item: Union[str, Iterable[str]]) -> str:
        if isinstance(item, str):
            return self.data.format(item)
        return self.data.format(", ".join(item))

    def __repr__(self) -> str:
        return repr(self.data.format("*"))

    def __str__(self) -> str:
        return str(self.data.format("*"))
