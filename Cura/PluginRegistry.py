import PluginError

import imp
import os

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
        
        module = self._findPlugin(name)
        if not module:
            raise PluginError.PluginNotFoundError(name)
            
        try:
            module.register()
        except PluginError as e:
            print(e)
        except AttributeError as e:
            print(e)
    
    # Load a set of plugins of a certain type
    # \param type The type of plugin to load
    def loadPlugins(self, type):
        for folder in self._pluginLocations:
            #for each entry, load plugin
            pass
    
    # Get the metadata for a certain plugin
    # \param name The name of the plugin
    def getMetaData(self, name):
        return self._metaData[name]
    
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
        pluginNames = []
        for folder in self._pluginLocations:
            #find plugins in folder and load metadata
            for name in os.listdir(folder):
                root, ext = os.path.splitext(name)
                if ext == '.py':
                    pluginNames.append(os.path.basename(root))

        for name in pluginNames:
            plugin = self._findPlugin(name)
            
            if not plugin:
                continue
            
            #try:
                #file, path, desc = imp.find_module(name, self._pluginLocations)
            #except ImportError:
                #continue
            
            #module = None
            #try:
                #module = imp.load_module(name, file, path, desc)
            #except ImportError:
                #continue
            #finally:
                #pass
                ##if file:
                    ##os.close(file)
            
            try:
                self._metaData[name] = plugin.getMetaData()
            except AttributeError as e:
                print(e)
                continue
            
                
    
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
    