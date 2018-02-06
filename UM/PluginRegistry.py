# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import imp
import os
import shutil  # For deleting plugin directories;
import stat    # For setting file permissions correctly;
import zipfile

from UM.Preferences import Preferences
from UM.PluginError import PluginNotFoundError, InvalidMetaDataError
from UM.Logger import Logger
from typing import Callable, Any, Optional, types, Dict, List

from PyQt5.QtCore import QObject, pyqtSlot, QUrl, pyqtProperty, pyqtSignal

from UM.Resources import Resources
from UM.PluginObject import PluginObject  # For type hinting
from UM.Platform import Platform
from UM.Version import Version

from UM.i18n import i18nCatalog
import json
i18n_catalog = i18nCatalog("uranium")


##  A central object to dynamically load modules as plugins.
#
#   The PluginRegistry class can load modules dynamically and use
#   them as plugins. Each plugin module is expected to be a directory with
#   and `__init__` file defining a `getMetaData` and a `register` function.
#
#   For more details, see the [plugins] file.
#
#   [plugins]: docs/plugins.md

class PluginRegistry(QObject):
    APIVersion = 4

    def __init__(self, parent = None):
        super().__init__(parent)

        self._all_plugins = []        # type: Dict[str, PluginObject]
        self._metadata = {}           # type: Dict[str, Dict[str, any]]

        self._plugins_available = []  # type: List[str]
        self._plugins_installed = []  # type: List[str]

        # NOTE: The disabled_plugins is explicitly set to None. When actually
        # loading the preferences, it's set to a list. This way we can see the
        # difference between no list and an empty one.
        self._disabled_plugins = None # type: Optional[List[str]]

        # Keep track of which plugins are 3rd-party
        self._plugins_external = []   # type: List[str]


        self._plugins = {}            # type: Dict[str, types.ModuleType]
        self._plugin_objects = {}     # type: Dict[str, PluginObject]

        self._plugin_locations = []  # type: List[str]
        self._folder_cache = {}      # type: Dict[str, str]

        self._application = None
        self._supported_file_types = {"umplugin": "Uranium Plugin"}
        preferences = Preferences.getInstance()
        preferences.addPreference("general/disabled_plugins", "")
# TODO:
# - [ ] Improve how metadata is stored. It should not be in the 'plugin' prop
#       of the dictionary item.
# - [ ] Remove usage of "active" in favor of "enabled".
# - [ ] Switch self._disabled_plugins to self._plugins_disabled
# - [ ] External plugins only appear in installed after restart
#
# NOMENCLATURE:
# Enabled (active):  A plugin which is installed and currently enabled.
# Disabled: A plugin which is installed but not currently enabled.
# Available: A plugin which is not installed but could be.
# Installed: A plugin which is installed locally in Cura.

#===============================================================================
# PUBLIC METHODS
#===============================================================================

    #   If used, this can add available plugins (from a remote server) to the
    #   registry. Cura uses this method to add 3rd-party plugins.
    def addExternalPlugins(self, plugin_list):

        for plugin in plugin_list:
            # Add the plugin id to the the all plugins list if not already there:
            if plugin["id"] not in self._all_plugins:
                self._all_plugins.append(plugin["id"])

                # Does this look redundant?
                # It is. Should be simplfied in the future but changing it right
                # now may break other functionality.
                if plugin["id"] not in self._plugins_available:
                    self._plugins_available.append(plugin["id"])
            self._metadata[plugin["id"]] = {
                "id": plugin["id"],
                "plugin": plugin,
                "update_url": plugin["file_location"]
            }

            # Keep a note of plugins which are not Ultimaker plugins:
            if plugin["id"] not in self._plugins_external:
                self._plugins_external.append(plugin["id"])

    #   Add a plugin location to the list of locations to search:
    def addPluginLocation(self, location: str):
        #TODO: Add error checking!
        self._plugin_locations.append(location)

    #   Check if all required plugins are loaded:
    def checkRequiredPlugins(self, required_plugins: List[str]):
        plugins = self._findInstalledPlugins()
        for plugin_id in required_plugins:
            if plugin_id not in plugins:
                Logger.log("e", "Plugin %s is required, but not added or loaded", plugin_id)
                return False
        return True

    #   Remove plugin from the list of enabled plugins and save to preferences:
    def disablePlugin(self, plugin_id: str):
        if plugin_id not in self._disabled_plugins:
            self._disabled_plugins.append(plugin_id)
        Preferences.getInstance().setValue("general/disabled_plugins", ",".join(self._disabled_plugins))

    #   Add plugin to the list of enabled plugins and save to preferences:
    def enablePlugin(self, plugin_id: str):
        if plugin_id in self._disabled_plugins:
            self._disabled_plugins.remove(plugin_id)
        Preferences.getInstance().setValue("general/disabled_plugins", ",".join(self._disabled_plugins))

    #   Get a list of enabled plugins:
    def getActivePlugins(self):
        plugin_list = []
        for plugin_id in self._all_plugins:
            if self.isActivePlugin(plugin_id):
                plugin_list.append(plugin_id)
        return plugin_list

    #   Get a list of available plugins (ones which are not yet installed):
    def getAvailablePlugins(self):
        return self._plugins_available

    #   Get a list of all metadata matching a certain subset of metadata:
    #   \param kwargs Keyword arguments.
    #       Possible keywords:
    #       - filter: \type{dict} The subset of metadata that should be matched.
    #       - active_only: Boolean, True when only active plugin metadata should
    #         be returned.
    def getAllMetaData(self, **kwargs):
        data_filter = kwargs.get("filter", {})
        active_only = kwargs.get("active_only", False)
        metadata_list = []
        for plugin_id in self._all_plugins:
            if active_only and plugin_id in self._disabled_plugins:
                continue
            plugin_metadata = self.getMetaData(plugin_id)
            if self._subsetInDict(plugin_metadata, data_filter):
                metadata_list.append(plugin_metadata)
        return metadata_list

    #   Get a list of disabled plugins:
    def getDisabledPlugins(self):
        return self._disabled_plugins

    def getExternalPlugins(self):
        return self._plugins_external

    #   Get a list of installed plugins:
    #   NOTE: These are plugins which have already been registered. This list is
    #         actually populated by the private _findInstalledPlugins() method.
    def getInstalledPlugins(self):
        return self._plugins_installed

    #   Get the singleton instance of this class:
    @classmethod
    def getInstance(cls) -> "PluginRegistry":
        if not cls._instance:
            cls._instance = PluginRegistry()
        return cls._instance

    #   Get the metadata for a certain plugin:
    #   NOTE: InvalidMetaDataError is raised when no metadata can be found or
    #         the metadata misses the right keys.
    def getMetaData(self, plugin_id: str):
        if plugin_id not in self._metadata:
            try:
                if not self._populateMetaData(plugin_id):
                    return {}
            except InvalidMetaDataError:
                return {}

        return self._metadata[plugin_id]

    #   Get the list of plugin locations:
    def getPluginLocations(self):
        return self._plugin_locations

    @pyqtSlot(str, result="QVariantMap")
    def installPlugin(self, plugin_path: str):
        Logger.log("d", "Install plugin got path: %s", plugin_path)
        plugin_path = QUrl(plugin_path).toLocalFile()
        Logger.log("i", "Attempting to install a new plugin %s", plugin_path)
        local_plugin_path = os.path.join(Resources.getStoragePath(Resources.Resources), "plugins")
        plugin_folder = ""
        result = {"status": "error", "message": "", "id": ""}
        success_message = i18n_catalog.i18nc("@info:status", "The plugin has been installed.\nPlease re-start the application to activate the plugin.")

        try:
            with zipfile.ZipFile(plugin_path, "r") as zip_ref:
                plugin_id = None
                for file in zip_ref.infolist():
                    if file.filename.endswith("/"):
                        plugin_id = file.filename.strip("/")
                        break

                if plugin_id is None:
                    result["message"] = i18n_catalog.i18nc("@info:status", "Failed to install plugin from <filename>{0}</filename>:\n<message>{1}</message>", plugin_path, "Invalid plugin archive.")
                    return result
                result["id"] = plugin_id
                plugin_folder = os.path.join(local_plugin_path, plugin_id)

                if os.path.isdir(plugin_folder):  # Plugin is already installed by user (so not a bundled plugin)
                    with zip_ref.open(plugin_id + "/plugin.json") as metadata_file:
                        metadata = json.loads(metadata_file.read().decode("utf-8"))

                    if "version" in metadata:
                        new_version = Version(metadata["version"])
                        old_version = Version(self.getMetaData(plugin_id)["plugin"]["version"])
                        if new_version > old_version:
                            for info in zip_ref.infolist():
                                extracted_path = zip_ref.extract(info.filename, path = plugin_folder)
                                permissions = os.stat(extracted_path).st_mode
                                os.chmod(extracted_path, permissions | stat.S_IEXEC) #Make these files executable.
                            result["status"] = "ok"
                            result["message"] = success_message
                            return result

                    Logger.log("w", "The plugin was already installed. Unable to install it again!")
                    result["status"] = "duplicate"
                    result["message"] = i18n_catalog.i18nc("@info:status", "Failed to install the plugin;\n<message>{0}</message>", "Plugin was already installed")
                    return result
                elif plugin_id in self._plugins:
                    # Plugin is already installed, but not by the user (eg; this is a bundled plugin)
                    # TODO: Right now we don't support upgrading bundled plugins at all, but we might do so in the future.
                    result["message"] = i18n_catalog.i18nc("@info:status", "Failed to install the plugin;\n<message>{0}</message>", "Unable to upgrade or install bundled plugins.")
                    return result

                for info in zip_ref.infolist():
                    extracted_path = zip_ref.extract(info.filename, path = plugin_folder)
                    permissions = os.stat(extracted_path).st_mode
                    os.chmod(extracted_path, permissions | stat.S_IEXEC) #Make these files executable.

        except: # Installing a new plugin should never crash the application.
            Logger.logException("d", "An exception occurred while installing plugin {path}".format(path = plugin_path))

            result["message"] = i18n_catalog.i18nc("@info:status", "Failed to install plugin from <filename>{0}</filename>:\n<message>{1}</message>", plugin_folder, "Invalid plugin file")
            return result

        # Installed plugins are kept on the list, so don't remove from available
        # self._plugins_available.remove(plugin_id);
        self._plugins_installed.append(plugin_id)

        if plugin_id in self._disabled_plugins:
            self._disabled_plugins.remove(plugin_id)

        result["status"] = "ok"
        result["message"] = success_message
        return result

    #   Check by ID if a plugin is active (enabled):
    def isActivePlugin(self, plugin_id):
        if plugin_id not in self._disabled_plugins:
            return True
        return False

    #   Check by ID if a plugin is availbable:
    def isAvailablePlugin(self, plugin_id: str):
        return plugin_id in self._plugins_available

    #   Check by ID if a plugin is disabled:
    def isDisabledPugin(self, plugin_id: str):
        if plugin_id in self._disabled_plugins:
            return True
        return false

    #   Check by ID if a plugin is installed:
    def isInstalledPlugin(self, plugin_id: str):
        return plugin_id in self._plugins_installed

    ##  Load all plugins matching a certain set of metadata
    #   \param meta_data \type{dict} The meta data that needs to be matched.
    #   \sa loadPlugin
    #   NOTE: This is the method which kicks everything off at app launch.
    def loadPlugins(self, metadata: Optional[dict] = None):

        # Get a list of all installed plugins:
        plugin_ids = self._findInstalledPlugins()
        for plugin_id in plugin_ids:

            # Get the plugin metadata:
            plugin_metadata = self.getMetaData(plugin_id)

            # Add the plugin to the list:
            self._all_plugins.append(plugin_id)
            self._plugins_installed.append(plugin_id)

            # Save all metadata to the metadata dictionary:
            self._metadata[plugin_id] = plugin_metadata
            if metadata is None or self._subsetInDict(self._metadata[plugin_id], metadata):
                #
                try:
                    self.loadPlugin(plugin_id)
                except PluginNotFoundError:
                    pass

    #   Load a single plugin by ID:
    def loadPlugin(self, plugin_id: str):

        # If plugin has already been loaded, do not load it again:
        if plugin_id in self._plugins:
            Logger.log("w", "Plugin %s was already loaded", plugin_id)
            return

        # If the list of disabled plugins doesn't exist yet, create it from
        # saved preferences:
        if not self._disabled_plugins:
            self._disabled_plugins = Preferences.getInstance().getValue("general/disabled_plugins").split(",")

        # If the plugin is in the list of disabled plugins, alert and return:
        if plugin_id in self._disabled_plugins:
            Logger.log("d", "Plugin %s was disabled", plugin_id)
            return

        # Find the actual plugin on drive:
        plugin = self._findPlugin(plugin_id)

        # If not found, raise error:
        if not plugin:
            raise PluginNotFoundError(plugin_id)

        # If found, but isn't in the metadata dictionary, add it:
        if plugin_id not in self._metadata:
            try:
                self._populateMetaData(plugin_id)
            except InvalidMetaDataError:
                return
        if self._metadata[plugin_id].get("plugin", {}).get("api", 0) != self.APIVersion:
            Logger.log("i", "Plugin %s uses an incompatible API version, ignoring", plugin_id)
            return
        try:
            to_register = plugin.register(self._application)
            if not to_register:
                Logger.log("e", "Plugin %s did not return any objects to register", plugin_id)
                return
            for plugin_type, plugin_object in to_register.items():
                if type(plugin_object) == list:
                    for nested_plugin_object in plugin_object:
                        self._addPluginObject(nested_plugin_object, plugin_id, plugin_type)
                else:
                    self._addPluginObject(plugin_object, plugin_id, plugin_type)

            self._plugins[plugin_id] = plugin
            self.enablePlugin(plugin_id)
            Logger.log("i", "Loaded plugin %s", plugin_id)

        except KeyError as e:
            Logger.log("e", "Error loading plugin %s:", plugin_id)
            Logger.log("e", "Unknown plugin type: %s", str(e))
        except Exception as e:
            Logger.logException("e", "Error loading plugin %s:", plugin_id)

    #   Set the central application object:
    def setApplication(self, app):
        self._application = app

    #   Uninstall a plugin with a given ID:
    @pyqtSlot(str, result="QVariantMap")
    def uninstallPlugin(self, plugin_id: str):
        Logger.log("d", "Uninstall plugin got ID: %s", plugin_id)
        plugin_folder = os.path.join(Resources.getStoragePath(Resources.Resources), "plugins")
        plugin_path = os.path.join(plugin_folder, plugin_id)
        Logger.log("i", "Attempting to uninstall %s", plugin_path)
        result = {"status": "error", "message": "", "id": plugin_id}
        success_message = i18n_catalog.i18nc("@info:status", "The plugin has been removed.\nPlease re-start the application to finish uninstall.")

        try:
            # Remove the files from the plugins directory:
            shutil.rmtree(plugin_path)

            # Remove the plugin object from the Plugin Registry:
            self._plugins.pop(plugin_id, None)
            self._plugins_installed.remove(plugin_id)
            # Remove the metadata from the Plugin Registry:
            # self._metadata[plugin_id] = {}

        except:
            Logger.logException("d", "An exception occurred while uninstalling %s", plugin_path)

            result["message"] = i18n_catalog.i18nc("@info:status", "Failed to uninstall plugin");
            return result

        result["status"] = "ok"
        result["message"] = success_message
        return result

#===============================================================================
# PRIVATE METHODS
#===============================================================================

    #   Returns a list of all possible plugin ids in the plugin locations:
    def _findInstalledPlugins(self, paths = None):
        plugin_ids = []

        if not paths:
            paths = self._plugin_locations

        for folder in paths:
            if not os.path.isdir(folder):
                continue

            for file in os.listdir(folder):
                filepath = os.path.join(folder, file)
                if os.path.isdir(filepath):
                    if os.path.isfile(os.path.join(filepath, "__init__.py")):
                        plugin_ids.append(file)
                    else:
                        plugin_ids += self._findInstalledPlugins([filepath])

        return plugin_ids

    ##  Try to find a module implementing a plugin
    #   \param plugin_id \type{string} The name of the plugin to find
    #   \returns module \type{module} if it was found None otherwise
    def _findPlugin(self, plugin_id: str) -> types.ModuleType:
        location = None
        for folder in self._plugin_locations:
            location = self._locatePlugin(plugin_id, folder)
            if location:
                break

        if not location:
            return None

        try:
            file, path, desc = imp.find_module(plugin_id, [location])
        except Exception:
            Logger.logException("e", "Import error when importing %s", plugin_id)
            return None

        try:
            module = imp.load_module(plugin_id, file, path, desc)
        except Exception:
            Logger.logException("e", "Import error loading module %s", plugin_id)
            return None
        finally:
            if file:
                os.close(file)

        return module

    def _locatePlugin(self, plugin_id: str, folder: str) -> Optional[str]:
        if not os.path.isdir(folder):
            return None

        if folder not in self._folder_cache:
            sub_folders = []
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isdir(file_path):
                    entry = (file, file_path)
                    sub_folders.append(entry)
            self._folder_cache[folder] = sub_folders

        for (file, file_path) in self._folder_cache[folder]:
            if file == plugin_id and os.path.exists(os.path.join(file_path, "__init__.py")):
                return folder
            else:
                file_path = self._locatePlugin(plugin_id, file_path)
                if file_path:
                    return file_path

        return None

    ##  private:
    #   Populate the list of metadata
    #   \param plugin_id \type{string}
    #   \return
    def _populateMetaData(self, plugin_id: str) -> bool:
        plugin = self._findPlugin(plugin_id)
        if not plugin:
            Logger.log("w", "Could not find plugin %s", plugin_id)
            return False

        meta_data = None

        location = None
        for folder in self._plugin_locations:
            location = self._locatePlugin(plugin_id, folder)
            if location:
                break

        if not location:
            Logger.log("w", "Could not find plugin %s", plugin_id)
            return False
        location = os.path.join(location, plugin_id)

        try:
            meta_data = plugin.getMetaData()

            metadata_file = os.path.join(location, "plugin.json")
            try:
                with open(metadata_file, "r") as f:
                    try:
                        meta_data["plugin"] = json.loads(f.read())
                    except json.decoder.JSONDecodeError:
                        Logger.logException("e", "Failed to parse plugin.json for plugin %s", plugin_id)
                        raise InvalidMetaDataError(plugin_id)

                    # Check if metadata is valid;
                    if "version" not in meta_data["plugin"]:
                        Logger.log("e", "Version must be set!")
                        raise InvalidMetaDataError(plugin_id)

                    if "i18n-catalog" in meta_data["plugin"]:
                        # A catalog was set, try to translate a few strings
                        i18n_catalog = i18nCatalog(meta_data["plugin"]["i18n-catalog"])
                        if "name" in meta_data["plugin"]:
                             meta_data["plugin"]["name"] = i18n_catalog.i18n(meta_data["plugin"]["name"])
                        if "description" in meta_data["plugin"]:
                            meta_data["plugin"]["description"] = i18n_catalog.i18n(meta_data["plugin"]["description"])

            except FileNotFoundError:
                Logger.logException("e", "Unable to find the required plugin.json file for plugin %s", plugin_id)
                raise InvalidMetaDataError(plugin_id)

        except AttributeError as e:
            Logger.log("e", "An error occurred getting metadata from plugin %s: %s", plugin_id, str(e))
            raise InvalidMetaDataError(plugin_id)

        if not meta_data:
            raise InvalidMetaDataError(plugin_id)

        meta_data["id"] = plugin_id
        meta_data["location"] = location

        # Application-specific overrides
        appname = self._application.getApplicationName()
        if appname in meta_data:
            meta_data.update(meta_data[appname])
            del meta_data[appname]

        self._metadata[plugin_id] = meta_data
        return True

    #   Check if a certain dictionary contains a certain subset of key/value pairs
    #   \param dictionary \type{dict} The dictionary to search
    #   \param subset \type{dict} The subset to search for
    def _subsetInDict(self, dictionary: Dict, subset: Dict) -> bool:
        for key in subset:
            if key not in dictionary:
                return False
            if subset[key] != {} and dictionary[key] != subset[key]:
                return False
        return True

#===============================================================================
# GRAVEYARD
# Methods in the graveyard are no longer used and can eventually be removed and
# forgotten by the ages. They aren't yet though because their memories still
# live on in the hearts of other classes.
#===============================================================================

    ##  Get a speficic plugin object given an ID. If not loaded, load it.
    #   \param plugin_id \type{string} The ID of the plugin object to get.
    def getPluginObject(self, plugin_id: str) -> PluginObject:
        if plugin_id not in self._plugins:
            self.loadPlugin(plugin_id)
        return self._plugin_objects[plugin_id]

    # Plugin object stuff is definitely considered depreciated.
    def _addPluginObject(self, plugin_object: PluginObject, plugin_id: str, plugin_type: str):
        plugin_object.setPluginId(plugin_id)
        self._plugin_objects[plugin_id] = plugin_object
        try:
            self._type_register_map[plugin_type](plugin_object)
        except Exception as e:
            Logger.logException("e", "Unable to add plugin %s", plugin_id)

    def addSupportedPluginExtension(self, extension, description):
        if extension not in self._supported_file_types:
            self._supported_file_types[extension] = description
            self.supportedPluginExtensionsChanged.emit()

    supportedPluginExtensionsChanged = pyqtSignal()

    @pyqtProperty("QStringList", notify=supportedPluginExtensionsChanged)
    def supportedPluginExtensions(self):
        file_types = []
        all_types = []

        if Platform.isLinux():
            for ext, desc in self._supported_file_types.items():
                file_types.append("{0} (*.{1} *.{2})".format(desc, ext.lower(), ext.upper()))
                all_types.append("*.{0} *.{1}".format(ext.lower(), ext.upper()))
        else:
            for ext, desc in self._supported_file_types.items():
                file_types.append("{0} (*.{1})".format(desc, ext))
                all_types.append("*.{0}".format(ext))

        file_types.sort()
        file_types.insert(0, i18n_catalog.i18nc("@item:inlistbox", "All Supported Types ({0})", " ".join(all_types)))
        file_types.append(i18n_catalog.i18nc("@item:inlistbox", "All Files (*)"))
        return file_types

    @pyqtSlot(str, result = bool)
    def isPluginFile(self, plugin_path: str):
        extension = os.path.splitext(plugin_path)[1].strip(".")
        if extension.lower() in self._supported_file_types.keys():
            return True
        return False

    ##  Get the path to a plugin.
    #
    #   \param plugin_id \type{string} The ID of the plugin.
    #   \return \type{string} The absolute path to the plugin or an empty string if the plugin could not be found.
    def getPluginPath(self, plugin_id: str) -> Optional[str]:
        if plugin_id in self._plugins:
            plugin = self._plugins[plugin_id]
        else:
            plugin = self._findPlugin(plugin_id)

        if not plugin:
            return None

        path = os.path.dirname(self._plugins[plugin_id].__file__)
        if os.path.isdir(path):
            return path

        return None

    ##  Add a new plugin type.
    #
    #   This function is used to add new plugin types. Plugin types are simple
    #   string identifiers that match a certain plugin to a registration function.
    #
    #   The callable `register_function` is responsible for handling the object.
    #   Usually it will add the object to a list of objects in the relevant class.
    #   For example, the plugin type 'tool' has Controller::addTool as register
    #   function.
    #
    #   `register_function` will be called every time a plugin of `type` is loaded.
    #
    #   \param type \type{string} The name of the plugin type to add.
    #   \param register_function \type{callable} A callable that takes an object as parameter.
    @classmethod
    def addType(cls, plugin_type: str, register_function: Callable[[Any], None]):
        cls._type_register_map[plugin_type] = register_function

    ##  Remove a plugin type.
    #
    #   \param type \type{string} The plugin type to remove.
    @classmethod
    def removeType(cls, plugin_type: str):
        if plugin_type in cls._type_register_map:
            del cls._type_register_map[plugin_type]



    _type_register_map = {}  # type: Dict[str, Callable[[Any], None]]
    _instance = None    # type: PluginRegistry
