from copy import deepcopy
from typing import Optional


class SQLFilter:
    """Dynamically change the SQL query. If no keywords arguments are provided when
    calling the instance it will use the default ones obtained by the SQLQuery from
    the owners instance.
    """

    def __init__(self, query: str, where: Optional[str] = None, **kwargs):
        self._query = query
        self._query_where = query
        self._default_kwargs = kwargs
        if where:
            self._query_where += " WHERE {where}"
            self._default_kwargs["where"] = where

    @property
    def query(self):
        """ The base query"""
        return self._query

    def __call__(self, query_all: bool = False, **kwargs):
        filter_kwargs = deepcopy(self._default_kwargs)
        filter_kwargs.update(kwargs)
        if query_all:
            return self._query.format(**filter_kwargs)
        else:
            return self._query_where.format(**filter_kwargs)

    def __repr__(self):
        return self._query.format(**self._default_kwargs)
