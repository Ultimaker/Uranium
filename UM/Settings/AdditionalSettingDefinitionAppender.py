# Copyright (c) 2023 UltiMaker.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict
from UM.PluginObject import PluginObject
from UM.Settings.SettingDefinition import DefinitionPropertyType, SettingDefinition


def prependIdToSettings(tag_type: str, tag_id: str, tag_version: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """ This takes the whole (extra) settings-map as defined by the provider, and returns a tag-renamed version.

    Additional (appended) settings will need to be prepended with (an) extra identifier(s)/namespaces to not collide.
    This is done for when there are multiple additional settings appenders that might not know about each other.
    This includes any formulas, which will also be included in the renaming process.

    Appended settings may not be the same as 'baseline' (so any 'non-appended' settings) settings.
    (But may of course clash between different providers and versions, that's the whole point of this function...)
    Furthermore, it's assumed that formulas within the appended settings will only use settings either;
     - as defined within the baseline, or;
     - any other settings defined _by the provider itself_.

    For each key that is renamed, this results in a mapping <key> -> _<provider_type>__<id*>__<version>__<key>
     where '<id*>' is the version of the provider, but converted from using points to using underscores.
    Example: 'tapdance_factor' might become '_plugin__dancingprinter__1_2_99__tapdance_factor'
    Also note that all the tag_... parameters will be forced to lower-case.

    :param tag_type: Type of the additional settings appender, for example; "PLUGIN".
    :param tag_id: ID of the provider. Should be unique.
    :param tag_version: Version of the provider. Points will be replaced by underscores.
    :param settings: The settings as originally provided.

    :returns: Remapped settings, where each settings-name is properly tagged/'namespaced'.
    """
    tag_type = tag_type.lower()
    tag_id = tag_id.lower()
    tag_version = tag_version.lower().replace(".", "_")

    # First get the mapping, so that both the 'headings' and formula's can be renamed at the same time later.
    def _getMapping(values: Dict[str, Any]) -> Dict[str, str]:
        result = {}
        for key, value in values.items():
            mapped_key = key
            if isinstance(value, dict):
                if "type" in value and value["type"] != "category":
                    mapped_key = f"_{tag_type}__{tag_id}__{tag_version}__{key}"
                result.update(_getMapping(value))
            result[key] = mapped_key
        return result
    key_map = _getMapping(settings)

    # Get all values that can be functions, so it's known where to replace.
    function_type_names = set(SettingDefinition.getPropertyNames(DefinitionPropertyType.Function))

    # Replace all, both as key-names and their use in formulas.
    def _doReplace(values: Dict[str, Any]) -> Dict[str, str]:
        result = {}
        for key, value in values.items():
            if key in function_type_names and isinstance(value, str):
                # Replace key-names in the specified settings-function.
                for original, mapped in key_map.items():
                    value = value.replace(original, mapped)
            elif isinstance(value, dict):
                # Replace key-name 'heading'.
                key = key_map.get(key, key)
                value = _doReplace(value)
            result[key] = value
        return result
    return _doReplace(settings)


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
