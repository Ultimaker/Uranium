from collections import defaultdict
from typing import Dict, Any


class WorkspaceMetadataStorage:
    def __init__(self) -> None:
        # We allow for a set of key value pairs to be stored per plugin.
        self._data = defaultdict(dict)  # type: Dict[str, Dict[str, Any]]

    def setEntryToStore(self, plugin_id: str, key: str, data: Any) -> None:
        self._data[plugin_id][key] = data

    def setAllData(self, data: Dict[str, Dict[str, Any]]) -> None:
        self._data = defaultdict(dict, data)

    def getAllData(self) -> Dict[str, Dict[str, Any]]:
        return self._data

    def getPluginMetadata(self, plugin_id: str) -> Dict[str, Any]:
        return self._data[plugin_id]

    def clear(self) -> None:
        self._data = defaultdict(dict)