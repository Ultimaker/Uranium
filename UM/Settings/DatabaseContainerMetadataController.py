from typing import Tuple, List, Generator, Optional, Any
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
        self.queries = queries
        self.cursor: Optional[Cursor] = None
        self.container_type: Optional[InstanceContainer] = None
        self._insert_batch: List[Tuple] = []

    def setupTable(self, cursor: Cursor) -> None:
        self.cursor = cursor
        self.cursor.executescript(self.queries.create)

    def insert(self, metadata: metadata_type) -> None:
        values = list(self.groomMetadata(metadata).values())
        self.cursor.execute(self.queries.insert, values)

    def update(self, metadata: metadata_type) -> None:
        self.cursor.execute(self.queries.update, metadata.values())

    def delete(self, container_id: str) -> None:
        self.cursor.execute(self.queries.delete, (container_id,))

    def keys(self) -> Generator:
        for key in self.queries.fields.keys():
            yield key
        yield "container_type"
        yield "type"

    def values(self, container_id: str) -> Generator:
        result = self.cursor.execute(self.queries.select, (container_id,)).fetchone()
        if result is None:
            Logger.warning(f"Could not retrieve metadata for: {container_id} from database")
            return []  # Todo: check if this needs to be None, empty list, raise an exception or fallback to old container
        for value in result:
            yield value
        yield self.container_type
        yield self.queries.table

    def items(self, container_id: str) -> Generator:
        for key, value in zip(self.keys(), self.values(container_id)):
            yield key, value

    def getMetadata(self, container_id: str) -> metadata_type:
        metadata = {k: v for k, v in self.items(container_id)}
        return metadata

    def groomMetadata(self, metadata: metadata_type) -> metadata_type:
        return {k: metadata.get(k, "") for k in self.queries.fields.keys()}
