from Cura.PluginError import PluginError, PluginNotFoundError, InvalidMetaDataError

import imp
import os

'''
\brief A central object to dynamically load modules as plugins.

The PluginRegistry class can load modules dynamically and use
them as plugins. Each plugin module is expected to be a directory with
and __init__ file defining a getMetaData and a register function. 

getMetaData should return a dictionary of metadata, with the "name" 
and "type" keys expected to be set. The register function is passed 
the application object as parameter and is expected to register the 
appropriate classes with the appropriate objects.

Plugins can be located in any location listed in the plugin locations.
The plugin locations are scanned recursively for plugins.

'''
class PluginRegistry(object):
    def __init__(self):
        self._plugins = {}
        self._meta_data = {}
        self._plugin_locations = []
        self._application = None
    
    # Load a single plugin by name
    # \param name The name of the plugin
    def loadPlugin(self, name):
        if name in self._plugins:
            # Already loaded, do not load again
            return
        
        plugin = self._findPlugin(name)
        if not plugin:
            raise PluginNotFoundError(name)
        
        if name not in self._meta_data:
            self._populateMetaData(name)
            
        try:
            plugin.register(self._application)
            self._plugins[name] = plugin
        except PluginError as e:
            print(e)
        except AttributeError as e:
            print(e)
    
    # Load all plugins matching a certain set of metadata
    # \param metaData The metaData that needs to be matched.
    def loadPlugins(self, metaData):
        pluginNames = self._findAllPlugins()
        
        for name in pluginNames:
            pluginData = self.getMetaData(name)
            
            if self._subsetInDict(pluginData, metaData):
                self.loadPlugin(name)

    # Get the metadata for a certain plugin
    # \param name The name of the plugin
    def getMetaData(self, name):
        if name not in self._meta_data:
            self._populateMetaData(name)

        return self._meta_data[name]
    
    # Get a list of all metadata matching a certain subset of metaData
    # \param metaData The subset of metadata that should be matched.
    def getAllMetaData(self, metaData):
        pluginNames = self._findAllPlugins()
        
        returnVal = []
        for name in pluginNames:
            pluginData = self.getMetaData(name)
            if self._subsetInDict(pluginData, metaData):
                returnVal.append(pluginData)
            
        return returnVal
    
    # Get the list of plugin locations
    def getPluginLocations(self):
        return self._plugin_locations
    
    # Add a plugin location to the list of locations to search
    # \param location The location to add to the list
    def addPluginLocation(self, location):
        #TODO: Add error checking!
        self._plugin_locations.append(location)
        
    # Set the central application object
    # This is used by plugins as a central access point for other objects
    # \param app The application object to use
    def setApplication(self, app):
        self._application = app
    
    # Private
    # Populate the list of metadata
    def _populateMetaData(self, name):
        #pluginNames = []
        #for folder in self._pluginLocations:
            ##find plugins in folder and load metadata
            #for name in os.listdir(folder):
                #if os.path.isdir(os.path.join(folder, name)):
                    #pluginNames.append(name)

        #for name in pluginNames:
        plugin = self._findPlugin(name)
        
        if not plugin:
            raise InvalidMetaDataError(name)
        
        metaData = None
        try:
            metaData = plugin.getMetaData()
        except AttributeError as e:
            print(e)
            return
        
        if not metaData or (not "name" in metaData and not "type" in metaData):
            raise InvalidMetaDataError(name)
        
        self._meta_data[name] = plugin.getMetaData()
            
                
    # Private
    # Try to find a module implementing a plugin
    # \param name The name of the plugin to find
    def _findPlugin(self, name):
        location = None
        for folder in self._plugin_locations:
            location = self._locatePlugin(name, folder)
        
        try:
            file, path, desc = imp.find_module(name, [ location ])
        except ImportError as e:
            return False
        
        try:
            module = imp.load_module(name, file, path, desc)
        except ImportError as e:
            return False
        finally:
            if file:
                os.close(file)
                        
        return module
    
    # Private
    # Returns a list of all possible plugin names in the plugin locations
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
    
    # Private
    # Try to find a directory we can use to load a plugin from
    # \param name The name of the plugin to locate
    # \param folder The base folder to look into
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
    
    # Private
    # Check if a certain dictionary contains a certain subset of key/value pairs
    # \param dictionary The dictionary to search
    # \param subset The subset to search for
    def _subsetInDict(self, dictionary, subset):
        for key, value in subset:
            if key not in dictionary:
                return False
            if dictionary[key] != value:
                return False
        return True
