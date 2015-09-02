# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import json
import collections
import os.path
from copy import deepcopy

from UM.Resources import Resources
from UM.Signal import Signal, SignalEmitter
from UM.Settings import SettingsError
from UM.Settings.Setting import Setting
from UM.Settings.SettingsCategory import SettingsCategory

from UM.i18n import i18nCatalog
uranium_catalog = i18nCatalog("uranium")

class MachineDefinition(SignalEmitter):
    MachineDefinitionVersion = 1
    UltimakerManufacturerString = "Ultimaker"
    OtherManufacturerString = "Other"

    def __init__(self, machine_manager, path):
        self._machine_manager = machine_manager

        self._path = path

        self._id = ""
        self._name = ""
        self._variant_name = ""
        self._manufacturer = ""
        self._author = ""
        self._visible = True
        self._pages = []

        self._machine_settings = []
        self._categories = []

        self._json_data = None
        self._loaded = False

    settingsLoaded = Signal()

    def getId(self):
        return self._id

    def getName(self):
        return self._name

    def getVariantName(self):
        return self._variant_name

    def getManufacturer(self):
        return self._manufacturer

    def getAuthor(self):
        return self._author

    def isVisible(self):
        return self._visible

    def getPages(self):
        return self._pages

    def hasVariants(self):
        return len(self._machine_manager.getAllMachineVariants(self._id)) > 1

    ##  Get the machine mesh (in most cases platform)
    #   Todo: Might need to rename this to get machine mesh?
    def getPlatformMesh(self):
        return self._platform_mesh

    def getPlatformTexture(self):
        return self._platform_texture

    def loadMetaData(self):
        # Should we clean up the loaded JSON data after reading metadata?
        # When we call loadALL the JSON data gets loaded and cleaned up in loadAll.
        # loadAll calls loadMetaData internally but we should not try to load the
        # JSON data again. So only perform the JSON data cleanup when we are not being
        # called by loadAll.
        clean_json = False
        if not self._json_data:
            clean_json = True
            with open(self._path, "rt", -1, "utf-8") as f:
                self._json_data = json.load(f, object_pairs_hook=collections.OrderedDict)

        if "id" not in self._json_data or "name" not in self._json_data or "version" not in self._json_data:
            raise SettingsError.InvalidFileError(self._path)

        if self._json_data["version"] != self.MachineDefinitionVersion:
            raise SettingsError.InvalidVersionError(self._path)

        if self._machine_manager.getApplicationName() in self._json_data:
            app_data = self._json_data[self._machine_manager.getApplicationName()]
            self._json_data[self._machine_manager.getApplicationName()] = None
            self._json_data.update(app_data)

        self._id = self._json_data["id"]
        self._name = self._json_data["name"]
        self._visible = self._json_data.get("visible", True)
        self._variant_name = self._json_data.get("variant", "")
        self._manufacturer = self._json_data.get("manufacturer", uranium_catalog.i18nc("@label", "Unknown Manufacturer"))
        self._author = self._json_data.get("author", uranium_catalog.i18nc("@label", "Unknown Author"))
        self._pages = self._json_data.get("pages", {})

        if clean_json:
            self._json_data = None

    def loadAll(self):
        if self._loaded:
            return

        with open(self._path, "rt", -1, "utf-8") as f:
            self._json_data = json.load(f, object_pairs_hook=collections.OrderedDict)

        if not self._name:
            self.loadMetaData()

        self._i18n_catalog = i18nCatalog(os.path.basename(self._path))

        self._platform_mesh = self._json_data.get("platform", "")
        self._platform_texture = self._json_data.get("platform_texture", "")

        if "inherits" in self._json_data:
            inherits_from = MachineDefinition(self._machine_manager, Resources.getPath(Resources.MachineDefinitions, self._json_data["inherits"]))
            inherits_from.loadAll()

            self._machine_settings = inherits_from._machine_settings
            self._categories = inherits_from._categories

        if "machine_settings" in self._json_data:
            for key, value in self._json_data["machine_settings"].items():
                setting = self.getSetting(key)
                if not setting:
                    setting = Setting(self._machine_manager, key, self._i18n_catalog)
                    self._machine_settings.append(setting)
                setting.fillByDict(value)

        if "categories" in self._json_data:
            for key, value in self._json_data["categories"].items():
                category = self.getSettingsCategory(key)
                if not category:
                    category = SettingsCategory(self._machine_manager, key, self._i18n_catalog, self)
                    self._categories.append(category)
                category.fillByDict(value)

        if "overrides" in self._json_data:
            for key, value in self._json_data["overrides"].items():
                setting = self.getSetting(key)
                if not setting:
                    continue

                setting.fillByDict(value)

        self.settingsLoaded.emit()

        #self._json_data = None
        self._loaded = True

    ##  Get setting category by key
    #   \param key Category key to get.
    #   \return category or None if key was not found.
    def getSettingsCategory(self, key):
        for category in self._categories:
            if category.getKey() == key:
                return category
        return None

    ##  Get all categories.
    #   \returns list of categories
    def getAllCategories(self):
        return self._categories

    ##  Get all settings of this machine
    #   \param kwargs Keyword arguments.
    #                 Possible values are:
    #                 * include_machine: boolean, True if machine settings should be included. Default False.
    #                 * visible_only: boolean, True if only visible settings should be included. Default False.
    #   \return list of settings
    def getAllSettings(self, **kwargs):
        all_settings = []
        if kwargs.get("include_machine", False):
            all_settings.extend(self._machine_settings)

        for category in self._categories:
            all_settings.extend(category.getAllSettings())

        if kwargs.get("visible_only"):
            all_settings = filter(lambda s: s.isVisible(), all_settings)

        return all_settings

    ##  Get machine settings of this machine (category less settings).
    #   \return list of settings
    def getMachineSettings(self):
        return self._machine_settings

    ##  Get setting by key.
    #   \param key Key to select setting by (string)
    #   \return Setting or none if no setting was found.
    def getSetting(self, key):
        for category in self._categories:
            setting = category.getSetting(key)
            if setting is not None:
                return setting
        for setting in self._machine_settings:
            setting = setting.getSetting(key)
            if setting is not None:
                return setting
        return None #No setting found

    def isSetting(self, key):
        return self.isUserSetting(key) or self.isMachineSetting(key)

    def isUserSetting(self, key):
        for category in self._categories:
            if category.getSetting(key):
                return True

        return False

    def isMachineSetting(self, key):
        for setting in self._machine_settings:
            if setting.getSetting(key):
                return True

        return False

    # Because Python sort is stupid and does not allow for specifying a comparison method
    def __lt__(self, other):
        # This makes sure we place Ultimaker machines at the top of the list and "Other" at the bottom
        if self._manufacturer == self.UltimakerManufacturerString and other.getManufacturer() != self.UltimakerManufacturerString:
            return True

        if self._manufacturer != self.UltimakerManufacturerString and other.getManufacturer() == self.UltimakerManufacturerString:
            return False

        if self._manufacturer == self.OtherManufacturerString and other.getManufacturer() != self.OtherManufacturerString:
            return False

        if self._manufacturer != self.OtherManufacturerString and other.getManufacturer() == self.OtherManufacturerString:
            return True

        # Otherwise, just sort by manufacturer and name
        if self._manufacturer < other.getManufacturer():
            return True
        elif self._manufacturer == other.getManufacturer():
            return self._name < other.getName()
        else:
            return False
