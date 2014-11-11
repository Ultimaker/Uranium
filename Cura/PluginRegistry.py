from Cura.PluginError import PluginError, PluginNotFoundError, InvalidMetaDataError

import imp
import os

class PluginRegistry(object):
    def __init__(self):
        self._plugins = {}
        self._metaData = {}
        self._pluginLocations = []
        self._application = None
    
    # Load a single plugin by name
    # \param name The name of the plugin
    def loadPlugin(self, name):
        if name in self._plugins:
            # Already loaded, do not load again
            return
        
        if not self._metaData:
            self._populateMetaData()
        
        plugin = self._findPlugin(name)
        if not plugin:
            raise PluginNotFoundError(name)
            
        try:
            plugin.register(self._application)
            self._plugins[name] = plugin
        except PluginError as e:
            print(e)
        except AttributeError as e:
            print(e)
    
    # Load a set of plugins of a certain type
    # \param type The type of plugin to load
    def loadPlugins(self, type):
        pluginNames = []
        for folder in self._pluginLocations:
            for file in os.listdir(folder):
                if os.path.isdir(file):
                    pluginNames.append(file)
                    
        for name in pluginNames:
            self.loadPlugin(name)

    # Get the metadata for a certain plugin
    # \param name The name of the plugin
    def getMetaData(self, name):
        if not self._metaData:
            self._populateMetaData()

        return self._metaData[name]
    
    # Get a list of metadata for a certain plugin type
    # \param type The type of plugin to get metadata for
    def getAllMetaData(self, type):
        if not self._metaData:
            self._populateMetaData()
            
        returnVal = []
        for data in self._metaData:
            if type in data and data["type"] == type:
                returnVal.append(data)
            
        return returnVal
    
    # Get the list of plugin locations
    def getPluginLocations(self):
        return self._pluginLocations
    
    # Add a plugin location to the list of locations to search
    # \param location The location to add to the list
    def addPluginLocation(self, location):
        #TODO: Add error checking!
        self._pluginLocations.append(location)
        
    # Set the central application object
    # This is used by plugins as a central access point for other objects
    # \param app The application object to use
    def setApplication(self, app):
        self._application = app
    
    # Private
    # Populate the list of metadata
    def _populateMetaData(self):
        pluginNames = []
        for folder in self._pluginLocations:
            #find plugins in folder and load metadata
            for name in os.listdir(folder):
                if os.path.isdir(os.path.join(folder, name)):
                    pluginNames.append(name)

        for name in pluginNames:
            plugin = self._findPlugin(name)
            
            if not plugin:
                print("Could not load plugin: " + name)
                continue
            
            metaData = None
            try:
                metaData = plugin.getMetaData()
            except AttributeError as e:
                print(e)
                continue
            
            if not metaData or (not "name" in metaData and not "type" in metaData):
                raise InvalidMetaDataError(name)
            
            self._metaData[name] = plugin.getMetaData()
            
                
    # Private
    # Try to find a module implementing a plugin
    # \param name The name of the plugin to find
    def _findPlugin(self, name):
        try:
            file, path, desc = imp.find_module(name, self._pluginLocations)
        except ImportError as e:
            print(e)
            return False
        
        try:
            module = imp.load_module(name, file, path, desc)
        except ImportError as e:
            print(e)
            return False
                        
        return module
    
