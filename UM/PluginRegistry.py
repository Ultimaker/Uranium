from UM.PluginError import PluginError, PluginNotFoundError, InvalidMetaDataError
from UM.Logger import Logger

import imp
import os

##  A central object to dynamically load modules as plugins.
#
#   The PluginRegistry class can load modules dynamically and use
#   them as plugins. Each plugin module is expected to be a directory with
#   and `__init__` file defining a `getMetaData` and a `register` function.
#
#   `getMetaData` should return a dictionary of metadata, with the "name"
#   and "type" keys expected to be set. The register function is passed
#   the application object as parameter and is expected to register the
#   appropriate classes with the appropriate objects.
#
#   Plugins can be located in any location listed in the plugin locations.
#   The plugin locations are scanned recursively for plugins.
class PluginRegistry(object):
    def __init__(self):
        super(PluginRegistry,self).__init__() # Call super to make multiple inheritence work.
        self._plugins = {}
        self._meta_data = {}
        self._plugin_locations = []
        self._application = None
        self._active_plugins = []
    
    #   Check if all required plugins are loaded. 
    #   \param required_plugins List of keys of all plugins that must be activated.
    def checkRequiredPlugins(self,required_plugins):
        plugin_names = self._findAllPlugins()
        for name in required_plugins:
            if name not in plugin_names:
                Logger.log('e', "Plugin %s is required, but not added or loaded",name)
                return False
        return True
    
    def getActivePlugins(self):
        return self._active_plugins
    
    ##  Remove pugin name from active list
    def removeActivePlugin(self,name):
        if name in self._active_plugins:
            self._active_plugins.remove(name)
    
    ##  Set a plugin to active
    def addActivePlugin(self, name):
        if name not in self._active_plugins:
            self._active_plugins.append(name)
    
    ##  Load a single plugin by name
    #   \param name \type{string} The name of the plugin
    #   \exception PluginNotFoundError Raised when the plugin could not be found.
    def loadPlugin(self, name):
        if name in self._plugins:
            # Already loaded, do not load again
            if(self._application is not None):
                Logger.log('w', 'Plugin %s was already loaded',name)
            return
        
        plugin = self._findPlugin(name)
        if not plugin:
            raise PluginNotFoundError(name)
        
        if name not in self._meta_data:
            self._populateMetaData(name)
            
        try:
            plugin.register(self._application)
            self.addActivePlugin(self.getMetaData(name)["name"]) #Use the name in meta data
            Logger.log('i', 'Loaded plugin %s', name)
            self._plugins[name] = plugin
        except PluginError as e:
            Logger.log('e', e)
        except AttributeError as e:
            Logger.log('e', e)
    
    ##  Load all plugins matching a certain set of metadata
    #   \param metaData \type{dict} The metaData that needs to be matched.
    #   \sa loadPlugin
    def loadPlugins(self, meta_data):
        plugin_names = self._findAllPlugins()
        
        for name in plugin_names:
            plugin_data = self.getMetaData(name)
            
            if self._subsetInDict(plugin_data, meta_data):
                self.loadPlugin(name)

    ##  Get the metadata for a certain plugin
    #   \param name \type{string} The name of the plugin
    #   \return \type{dict} The metadata of the plugin. Can be an empty dict.
    #   \exception InvalidMetaDataError Raised when no metadata can be found or the metadata misses the right keys.
    def getMetaData(self, name):
        if name not in self._meta_data:
            if not self._populateMetaData(name):
                return {}

        return self._meta_data[name]
    
    ##  Get a list of all metadata matching a certain subset of metaData
    #   \param metaData \type{dict} The subset of metadata that should be matched.
    #   \sa getMetaData
    def getAllMetaData(self, meta_data):
        plugin_names = self._findAllPlugins()
        
        return_values = []
        for name in plugin_names:
            plugin_data = self.getMetaData(name)
            if self._subsetInDict(plugin_data, meta_data):
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
    
    ## private:

    #   Populate the list of metadata
    def _populateMetaData(self, name):
        plugin = self._findPlugin(name)
        if not plugin:
            Logger.log('e', 'Could not find plugin %s', name)
            return False
        
        meta_data = None
        try:
            meta_data = plugin.getMetaData()
        except AttributeError as e:
            print(e)
            raise InvalidMetaDataError(name)

        if not meta_data or (not "name" in meta_data and not "type" in meta_data):
            raise InvalidMetaDataError(name)

        self._meta_data[name] = meta_data
        return True

    #   Try to find a module implementing a plugin
    #   \param name The name of the plugin to find
    #   \returns module if it was found None otherwise
    def _findPlugin(self, name):
        location = None
        for folder in self._plugin_locations:
            location = self._locatePlugin(name, folder)

        if not location:
            return None

        try:
            file, path, desc = imp.find_module(name, [ location ])
        except ImportError as e:
            Logger.log('e', "Import error when importing %s: %s", name, e)
            return False

        try:
            module = imp.load_module(name, file, path, desc)
        except ImportError as e:
            Logger.log('e', "Import error loading module %s: %s", name, e)
            return False
        finally:
            if file:
                os.close(file)

        return module
    
    #   Returns a list of all possible plugin names in the plugin locations
    def _findAllPlugins(self, paths = None):
        names = []
        
        if not paths:
            paths = self._plugin_locations
        
        for folder in paths:
            for file in os.listdir(folder):
                filepath = os.path.join(folder, file)
                if os.path.isdir(filepath):
                    if os.path.isfile(os.path.join(filepath, '__init__.py')):
                        names.append(file)
                    else:
                        names += self._findAllPlugins([ filepath ])
        return names
    
    #   Try to find a directory we can use to load a plugin from
    #   \param name The name of the plugin to locate
    #   \param folder The base folder to look into
    def _locatePlugin(self, name, folder):
        for file in os.listdir(folder):
            filepath = os.path.join(folder, file)
            if os.path.isdir(filepath):
                if file == name:
                    return folder
                else:
                    filepath = self._locatePlugin(name, filepath)
                    if filepath:
                        return filepath

        return False
    
    #   Check if a certain dictionary contains a certain subset of key/value pairs
    #   \param dictionary The dictionary to search
    #   \param subset The subset to search for
    def _subsetInDict(self, dictionary, subset):
        for key in subset:
            if key not in dictionary:
                return False
            if dictionary[key] != subset[key]:
                return False
        return True
