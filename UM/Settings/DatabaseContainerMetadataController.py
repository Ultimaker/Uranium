# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Tuple, List, Generator, Optional
from sqlite3 import Cursor

from UM.Logger import Logger
from UM.Settings.InstanceContainer import InstanceContainer

from .SQLQueryFactory import metadata_type, SQLQueryFactory


class DatabaseMetadataContainerController:
    """
    This is an interface for storing and retrieving container metadata from a database. Since each type of container
    has it's own metadata (and thus should probably insert / get / update it differently) it's likely that each type
    needs it's own controller.
    """

    def __init__(self, queries: SQLQueryFactory):
        self._queries = queries
        self.cursor: Optional[Cursor] = None
        self._container_type: Optional[InstanceContainer] = None
        self._insert_batch: List[Tuple] = []

    def _execute(self, *args) -> Cursor:
        if self.cursor:
            return self.cursor.execute(*args)
        else:
            Logger.error("Could not execute, cursor not set")
            raise RuntimeError("Could not execute, cursor not set")

    def setupTable(self, cursor: Cursor) -> None:
        """Creates the table in the DB.

        param cursor: the DB cursor
        """
        self.cursor = cursor
        self.cursor.executescript(self._queries.create)

    def insert(self, metadata: metadata_type) -> None:
        """Insert a container in the DB.

        param container_id: The container_id to insert
        """
        values = list(self.groomMetadata(metadata).values())
        self._execute(self._queries.insert, values)

    def update(self, metadata: metadata_type) -> None:
        """Updates a container in the DB.

        param container_id: The container_id to update
        """
        values = list(self.groomMetadata(metadata).values())
        values.append(metadata["id"])
        self._execute(self._queries.update, values)

    def delete(self, container_id: str) -> None:
        """Removes a container from the DB."""
        self._execute(self._queries.delete, (container_id,))

    def keys(self) -> Generator:
        """Yields all the metadata keys. These consist of the DB fields and `container_type` and `type`"""
        for key in self._queries.fields.keys():
            yield key
        yield "container_type"
        yield "type"

    def values(self, container_id: str) -> Generator:
        """Yields all value obtained from the DB row and the 'container_type' and `type`

        param container_id: The container_id to query
        """
        result = self._execute(self._queries.select, (container_id,)).fetchone()
        if result is None:
            Logger.warning(f"Could not retrieve metadata for: {container_id} from database")
            return []  # Todo: check if this needs to be None, empty list, raise an exception or fallback to old container
        for value in result:
            yield value
        yield self._container_type
        yield self._queries.table

    def items(self, container_id: str) -> Generator:
        """Yields all values and keys obtained from the DB row including the `container_type` and `type`
        param container_id: The container_id to query
        """
        for key, value in zip(self.keys(), self.values(container_id)):
            yield key, value

    def getMetadata(self, container_id: str) -> metadata_type:
        """Return the metadata needed to create a container

        param container_id: The container_id to query
        :return The container metadata
        """
        metadata = {k: v for k, v in self.items(container_id)}
        return metadata

    def groomMetadata(self, metadata: metadata_type) -> metadata_type:
        """
        Ensures that the metadata is in the order of the field keys and has the right size.
        if the metadata doesn't contains a key which is stored in the DB it will add it as
        an empty string. Key, value pairs that are not stored in the DB are dropped.

        :param metadata: The container metadata
        """
        return {k: metadata.get(k, "") for k in self._queries.fields.keys()}
