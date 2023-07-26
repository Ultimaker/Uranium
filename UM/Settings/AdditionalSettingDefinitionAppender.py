# Copyright (c) 2023 UltiMaker.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict
from UM.PluginObject import PluginObject


def prependIdToSettings(id: str, settings: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    result = {}
    for key, value in settings.items():
        if isinstance(value, dict):
            key = f"{id}:{key}" if ("type" in value and "category" not in value) else key
            value = prependIdToSettings(id, value)
        result[key] = value
    return result


class AdditionalSettingDefinitionsAppender(PluginObject):

    def __init__(self) -> None:
        super().__init__()

    def getAdditionalSettingDefinitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Should return the settings added by this plugin in json format.
        The settings should be divided by category (either existing or new ones).
        Settings in existing categories will be appended, new categories will be created.
        """
        raise NotImplementedError("A setting_definitions_appender needs to implement getAdditionalSettingDefinitions.")
