# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import imp
import os

from UM.PluginError import PluginNotFoundError, InvalidMetaDataError
from UM.Logger import Logger

##  A central object to dynamically load modules as plugins.
#
#   The PluginRegistry class can load modules dynamically and use
#   them as plugins. Each plugin module is expected to be a directory with
#   and `__init__` file defining a `getMetaData` and a `register` function.
#
#   For more details, see the [plugins] file.
#
#   [plugins]: docs/plugins.md
class PluginRegistry(object):
    APIVersion = 3

    def __init__(self):
        super().__init__()
        self._plugins = {}
        self._plugin_objects = {}
        self._meta_data = {}
        self._plugin_locations = []
        self._folder_cache = {}
        self._application = None
        self._active_plugins = []

    ##  Check if all required plugins are loaded.
    #   \param required_plugins \type{list} List of ids of plugins that ''must'' be activated.
    def checkRequiredPlugins(self, required_plugins):
        plugins = self._findAllPlugins()
        for plugin_id in required_plugins:
            if plugin_id not in plugins:
                Logger.log("e", "Plugin %s is required, but not added or loaded", plugin_id)
                return False
        return True

    ##  Get the list of active plugins.
    def getActivePlugins(self):
        return self._active_plugins

    ##  Ask whether plugin_name is an active plugin.
    #
    #   \param plugin_id \type{string} The id of the plugin which might be active or not.
    def isActivePlugin(self, plugin_id):
        return plugin_id in self._active_plugins

    ##  Remove plugin from the list of active plugins.
    #
    #   \param plugin_id \type{string} The id of the plugin to remove.
    def removeActivePlugin(self, plugin_id):
        if plugin_id in self._active_plugins:
            self._active_plugins.remove(plugin_id)

    ##  Add a plugin to the list of active plugins.
    #
    #   \param plugin_id \type{string} The id of the plugin to add.
    def addActivePlugin(self, plugin_id):
        if plugin_id not in self._active_plugins:
            self._active_plugins.append(plugin_id)

    ##  Load a single plugin by id
    #   \param plugin_id \type{string} The ID of the plugin, i.e. its directory name.
    #   \exception PluginNotFoundError Raised when the plugin could not be found.
    def loadPlugin(self, plugin_id):
        if plugin_id in self._plugins:
            # Already loaded, do not load again
            Logger.log("w", "Plugin %s was already loaded", plugin_id)
            return

        plugin = self._findPlugin(plugin_id)
        if not plugin:
            raise PluginNotFoundError(plugin_id)

        if plugin_id not in self._meta_data:
            self._populateMetaData(plugin_id)

        if self._meta_data[plugin_id].get("plugin", {}).get("api", 0) != self.APIVersion:
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
            self.addActivePlugin(plugin_id)
            Logger.log("i", "Loaded plugin %s", plugin_id)

        except KeyError as e:
            Logger.log("e", "Error loading plugin %s:", plugin_id)
            Logger.log("e", "Unknown plugin type: %s", str(e))
        except Exception as e:
            Logger.logException("e", "Error loading plugin %s:", plugin_id)

    def _addPluginObject(self, plugin_object, plugin_id, plugin_type):
        plugin_object.setPluginId(plugin_id)
        self._plugin_objects[plugin_id] = plugin_object
        try:
            self._type_register_map[plugin_type](plugin_object)
        except Exception as e:
            Logger.logException("e", "Unable to add plugin %s", id)

    ##  Load all plugins matching a certain set of metadata
    #   \param meta_data \type{dict} The meta data that needs to be matched.
    #   \sa loadPlugin
    def loadPlugins(self, meta_data = None): #pylint: disable=bad-whitespace
        plugins = self._findAllPlugins()

        for plugin_id in plugins:
            plugin_data = self.getMetaData(plugin_id)
            if meta_data is None or self._subsetInDict(plugin_data, meta_data):
                try:
                    self.loadPlugin(plugin_id)
                except PluginNotFoundError:
                    pass

    ##  Get a plugin object
    #   \param plugin_id \type{string} The ID of the plugin object to get.
    def getPluginObject(self, plugin_id):
        if plugin_id not in self._plugins:
            self.loadPlugin(plugin_id)
        return self._plugin_objects[plugin_id]

    ##  Get the metadata for a certain plugin
    #   \param plugin_id \type{string} The ID of the plugin
    #   \return \type{dict} The metadata of the plugin. Can be an empty dict.
    #   \exception InvalidMetaDataError Raised when no metadata can be found or the metadata misses the right keys.
    def getMetaData(self, plugin_id):
        if plugin_id not in self._meta_data:
            if not self._populateMetaData(plugin_id):
                return {}

        return self._meta_data[plugin_id]

    ##  Get the path to a plugin.
    #
    #   \param plugin_id \type{string} The ID of the plugin.
    #   \return \type{string} The absolute path to the plugin or an empty string if the plugin could not be found.
    def getPluginPath(self, plugin_id):
        plugin = None
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

    ##  Get a list of all metadata matching a certain subset of metadata
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - filter: \type{dict} The subset of metadata that should be matched.
    #                 - active_only: Boolean, True when only active plugin metadata should be returned.
    #   \sa getMetaData
    def getAllMetaData(self, **kwargs):
        data_filter = kwargs.get("filter", {})
        active_only = kwargs.get("active_only", False)

        plugins = self._findAllPlugins()
        return_values = []
        for plugin_id in plugins:
            if active_only and plugin_id not in self._active_plugins:
                continue

            plugin_data = self.getMetaData(plugin_id)
            if self._subsetInDict(plugin_data, data_filter):
                return_values.append(plugin_data)

        return return_values

    ##  Get the list of plugin locations
    #   \return \type{list} The plugin locations
    def getPluginLocations(self):
        return self._plugin_locations

    ##  Add a plugin location to the list of locations to search
    #   \param location \type{string} The location to add to the list
    def addPluginLocation(self, location):
        #TODO: Add error checking!
        self._plugin_locations.append(location)

    ##  Set the central application object
    #   This is used by plugins as a central access point for other objects
    #   \param app \type{Application} The application object to use
    def setApplication(self, app):
        self._application = app

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
    def addType(cls, plugin_type, register_function):
        cls._type_register_map[plugin_type] = register_function

    ##  Remove a plugin type.
    #
    #   \param type \type{string} The plugin type to remove.
    @classmethod
    def removeType(cls, plugin_type):
        if plugin_type in cls._type_register_map:
            del cls._type_register_map[plugin_type]

    ##  Get the singleton instance of this class.
    ##  \return instance \type{PluginRegistry}
    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = PluginRegistry()
        return cls._instance

    ##  private:
    #   Populate the list of metadata
    #   \param plugin_id \type{string}
    def _populateMetaData(self, plugin_id):
        plugin = self._findPlugin(plugin_id)
        if not plugin:
            Logger.log("e", "Could not find plugin %s", plugin_id)
            return False

        meta_data = None
        try:
            meta_data = plugin.getMetaData()
        except AttributeError as e:
            Logger.log("e", "An error occured getting metadata from plugin %s: %s", plugin_id, str(e))
            raise InvalidMetaDataError(plugin_id)

        if not meta_data:
            raise InvalidMetaDataError(plugin_id)

        meta_data["id"] = plugin_id

        # Application-specific overrides
        appname = self._application.getApplicationName()
        if appname in meta_data:
            meta_data.update(meta_data[appname])
            del meta_data[appname]

        self._meta_data[plugin_id] = meta_data
        return True

    ##   Try to find a module implementing a plugin
    #   \param plugin_id \type{string} The name of the plugin to find
    #   \returns module \type{module} if it was found None otherwise
    def _findPlugin(self, plugin_id):
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

    #   Returns a list of all possible plugin ids in the plugin locations
    def _findAllPlugins(self, paths = None): #pylint: disable=bad-whitespace
        ids = []

        if not paths:
            paths = self._plugin_locations

        for folder in paths:
            if not os.path.isdir(folder):
                continue

            for file in os.listdir(folder):
                filepath = os.path.join(folder, file)
                if os.path.isdir(filepath):
                    if os.path.isfile(os.path.join(filepath, "__init__.py")):
                        ids.append(file)
                    else:
                        ids += self._findAllPlugins([filepath])

        return ids

    #   Try to find a directory we can use to load a plugin from
    #   \param plugin_id \type{string} The id of the plugin to locate
    #   \param folder The base folder to look into
    def _locatePlugin(self, plugin_id, folder):
        if not os.path.isdir(folder):
            return None

        if folder not in self._folder_cache:
            sub_folders = []
            for file in os.listdir(folder):
                filepath = os.path.join(folder, file)
                if os.path.isdir(filepath):
                    entry = (file, filepath)
                    sub_folders.append(entry)
            self._folder_cache[folder] = sub_folders

        for (file, filepath) in self._folder_cache[folder]:
            if file == plugin_id and os.path.exists(os.path.join(filepath, "__init__.py")):
                return folder
            else:
                filepath = self._locatePlugin(plugin_id, filepath)
                if filepath:
                    return filepath

        return None

    #   Check if a certain dictionary contains a certain subset of key/value pairs
    #   \param dictionary \type{dict} The dictionary to search
    #   \param subset \type{dict} The subset to search for
    def _subsetInDict(self, dictionary, subset):
        for key in subset:
            if key not in dictionary:
                return False
            if subset[key] != {} and dictionary[key] != subset[key]:
                return False
        return True

    _type_register_map = {}
    _instance = None

