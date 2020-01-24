# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from collections import defaultdict
from typing import Dict, Union, List

basic_metadata_type = Union[str, int, float, bool, None]
full_metadata_type = Union[List[basic_metadata_type], basic_metadata_type, Dict[str, basic_metadata_type]]


from typing import Union, Dict, List


# modified from Original source: https://github.com/python/mypy/issues/731#issuecomment-539905783
# The recursive type doesn't seem to work for us. MyPy crashes with it. So this limits the type to 3 levels deep nesting.
JSONPrimitive = Union[str, int, bool, None]
JSONTypeLevel1 = Union[JSONPrimitive, Dict[str, JSONPrimitive], List[JSONPrimitive]]
JSONTypeLevel2 = Union[JSONPrimitive, Dict[str, JSONTypeLevel1], List[JSONTypeLevel1]]
JSONType = Union[JSONPrimitive, Dict[str, JSONTypeLevel2], List[JSONTypeLevel2]]


class WorkspaceMetadataStorage:
    #  The WorkspaceMetadataStorage, as the name implies, allows for plugins to store (and retrieve) extra information
    #   to a workspace. When a workspace is stored, all workspace readers will need to ensure that the workspace data
    #   is correctly stored to file. The same also holds when loading a workspace; the existing data will be cleared
    #   and replaced with the data recovered from the file (if any)
    def __init__(self) -> None:
        # We allow for a set of key value pairs to be stored per plugin.
        self._data = defaultdict(dict)  # type: Dict[str, Dict[str, JSONType]]

    def setEntryToStore(self, plugin_id: str, key: str, data: JSONType) -> None:
        self._data[plugin_id][key] = data

    def setAllData(self, data: Dict[str, Dict[str, JSONType]]) -> None:
        self._data = defaultdict(dict, data)

    def getAllData(self) -> Dict[str, Dict[str, JSONType]]:
        return self._data

    def getPluginMetadata(self, plugin_id: str) -> Dict[str, JSONType]:
        return self._data[plugin_id]

    def clear(self) -> None:
        self._data = defaultdict(dict)