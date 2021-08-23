from typing import Tuple, Dict, Any, List

metadata_type = Dict[str, Any]


class DatabaseMetadataContainerController:
    def __init__(self, insert_query: str = "", select_query: str = "" ,update_query: str = "", table_query: str = "") -> None:

        self._insert_batch: List[Tuple] = []

        self._insert_query = insert_query
        self._update_query = update_query
        self._table_query = table_query
        self._select_query = select_query

    def setupTable(self, cursor) -> None:
        cursor.execute(self._table_query)

    def _convertMetadataToInsertBatch(self, metadata: metadata_type) -> Tuple:
        raise NotImplementedError("Subclass of should provide way to convert metadata")

    def _convertRawDataToMetadata(self, data: Tuple) -> metadata_type:
        raise NotImplementedError("Subclass of should provide way to convert to metadata")

    def addToInsertBatch(self, metadata: metadata_type) -> None:
        self._insert_batch.append(self._convertMetadataToInsertBatch(metadata))

    def getMetadata(self, container_id: str, cursor) -> metadata_type:
        result = cursor.execute(self._select_query, (container_id,))
        data = result.fetchone()
        return self._convertRawDataToMetadata(data)

    def executeAllBatchedInserts(self, cursor) -> None:
        cursor.executemany(self._insert_query, self._insert_batch)
        self._insert_batch.clear()

    def insert(self, metadata: metadata_type, cursor) -> None:
        cursor.execute(self._insert_query, self._convertMetadataToInsertBatch(metadata))





