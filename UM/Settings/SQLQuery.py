import re

from .SQLFilter import SQLFilter


class SQLQuery:
    """ An SQL Query descriptor which ensures that the SQLFilters are properly initialized."""

    def __set_name__(self, owner, name):
        self._query = f"_{name}"

    def __get__(self, instance, owner):
        return getattr(instance, self._query)

    def __set__(self, instance, value: SQLFilter):
        kw = set(re.findall(self._pattern, value.query))
        hidden_kw = kw.difference({"table", "where"})
        kwargs = {"table": getattr(instance, "table")}
        if len(hidden_kw):
            kwargs.update({k: getattr(instance, f"{self._query}_{k}") for k in hidden_kw})
        getattr(value, "_default_kwargs").update(kwargs)
        setattr(instance, self._query, value)

    _pattern = re.compile("\{(.+?)\}")
