import Plugin

class PluginRegistry(object):
    def __init__(self):
        self._plugins = {}
        self._metaData = {}
        self._pluginLocations = []
        pass
    
    # Load a single plugin by name
    # \param name The name of the plugin
    def loadPlugin(self, name):
        if name in self._plugins:
            return self._plugins[name]
        
        location = self._findPlugin(name)
        if not location:
            raise FileNotFoundError("Could not find plugin {name}")
            
        plugin = None
        #TODO: Instantiate plugin at location
        return plugin
    
    # Load a set of plugins of a certain type
    # \param type The type of plugin to load
    def loadPlugins(self, type):
        for folder in self._pluginLocations:
            #for each entry, load plugin
            pass
    
    # Get the metadata for a certain plugin
    # \param name The name of the plugin
    def getMetaData(self, name):
        pass
    
    # Get a list of metadata for a certain plugin type
    # \param type The type of plugin to get metadata for
    def getAllMetaData(self, type):
        pass
    
    # Get the list of plugin locations
    def getPluginLocations(self):
        return self._pluginLocations
    
    # Add a plugin location to the list of locations to search
    # \param location The location to add to the list
    def addPluginLocation(self, location):
        #TODO: Add error checking!
        self._pluginLocations.append(location)
    
    # Private
    # Populate the list of metadata
    def _populateMetaData(self):
        for folder in self._pluginLocations:
            #TODO: find plugins in folder and load metadata
            pass
    
    def _findPlugin(self, name):
        for folder in self._pluginLocations:
            #TODO: Implement find plugins and read class
            pass
            
    