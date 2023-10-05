# Copyright (c) 2023 UltiMaker.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
from pathlib import Path
import os.path
from typing import Any, Dict, List

from UM.i18n import i18nCatalog
from UM.Logger import Logger
from UM.PluginObject import PluginObject
from UM.Settings.SettingDefinition import DefinitionPropertyType, SettingDefinition


class AdditionalSettingDefinitionsAppender(PluginObject):
    """
    This class is a way for plugins to append additional settings, not defined by/for the main program itself.

    Each plugin needs to register as either a 'setting_definitions_appender' or 'backend_plugin'.

    Any implementation also needs to fill 'self.definition_file_paths' with a list of files with setting definitions.
    Each file should be a json list of setting categories, either matching existing names, or be a new category.
    Each category and setting has the same json structure as the main settings otherwise.

    It's also possible to set the 'self.appender_type', if there are many kinds of plugins to implement this,
    in order to prevent name-clashes.

    Lastly, if setting-definitions are to be made on the fly by the plugin, override 'getAdditionalSettingDefinitions',
    instead of providing the files. This should then return a dict, as if parsed by json.
    """

    def __init__(self, catalog: i18nCatalog = None) -> None:
        super().__init__()
        self.appender_type = "PLUGIN"
        self.definition_file_paths: List[Path] = []
        self._catalog = catalog

    def getAppenderType(self) -> str:
        """
        Return an extra identifier prepended to the setting internal id, to prevent name-clashes with other plugins.
        """
        return self.appender_type

    def getAdditionalSettingDefinitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Return the settings added by this plugin in json format.
        Put values in self.definition_file_paths if you wish to load from files, or override this function otherwise.

        The settings should be divided by category (either existing or new ones).
        Settings in existing categories will be appended, new categories will be created.

        Setting names (not labels) will be post-processed ('mangled') internally to prevent name-clashes.
        NOTE: The 'mangled' names are also the ones send out to any backend!
        (See the _prependIdToSettings function below for a more precise explanation.)

        :return: Dictionary of settings-categories, containing settings-definitions (with post-processed names).
        """
        result = {}
        for path in self.definition_file_paths:
            if not os.path.exists(path):
                Logger.error(f"File {path} with additional settings for '{self.getId()}' doesn't exist.")
                continue
            try:
                with open(path, "r", encoding = "utf-8") as definitions_file:
                    result.update(json.load(definitions_file))
            except OSError as oex:
                Logger.error(f"Could not read additional settings file for '{self.getId()}' because: {str(oex)}")
                continue
            except json.JSONDecodeError as jex:
                Logger.error(f"Could not parse additional settings provided by '{self.getId()}' because: {str(jex)}")
                continue
        return self._prependIdToSettings(result)

    def _prependIdToSettings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """ This takes the whole (extra) settings-map as defined by the provider, and returns a tag-renamed version.

        Note that this function also translates the (label and description of the) settings, if a catalog is present.

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
        tag_type = self.getAppenderType().lower()
        tag_id = self.getId().lower()
        tag_version = self.getVersion().lower().replace(".", "_")

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

        # Get all values that can be functions (or need to be translated), so it's known where to replace.
        function_type_names = set(SettingDefinition.getPropertyNames(DefinitionPropertyType.Function))
        translation_type_names = set(SettingDefinition.getPropertyNames(DefinitionPropertyType.TranslatedString))

        # Replace all, both as key-names and their use in formulas.
        def _doReplace(values: Dict[str, Any], original_parent_name: str = "") -> Dict[str, str]:
            result = {}
            for key, value in values.items():
                if key in function_type_names and isinstance(value, str):
                    # Replace key-names in the specified settings-function.
                    for original, mapped in key_map.items():
                        value = value.replace(original, mapped)
                elif key in translation_type_names and self._catalog is not None:
                    value = self._catalog.i18nc(f"{original_parent_name} {key}", value)
                elif isinstance(value, dict):
                    # Replace key-name 'heading'.
                    original_key = key
                    key = key_map.get(key, key)
                    value = _doReplace(value, original_key)
                result[key] = value
            return result

        return _doReplace(settings)
