from Cura.InputDevice import InputDevice
from Cura.View.View import View
from Cura.Tool import Tool
from Cura.Scene.Scene import Scene

## Glue glass that holds the scene, (active) view(s), (active) tool(s) and possible user inputs.
#
#  The different types of views / tools / inputs are defined by plugins.
class Controller(object):
    def __init__(self):
        super(Controller, self).__init__()
        self._active_tool = None
        self._tools = {}
        
        self._input_devices = {}
        
        self._active_view = None
        self._views = {}
        self._scene = Scene()
    
    ## Add a view by name if it's not already added.
    #  \param name Unique identifier of view (usually the plugin name)
    #  \param view The view to be added
    def addView(self, name, view):
        if(name not in self._views):
            self._views[name] = view
    
    ## Request view by name. Returns None if no view is found.
    #  \param name Unique identifier of view (usually the plugin name)
    #  \return View if name was found, none otherwise.
    def getView(self, name):
        try:
            return self._views[name]
        except KeyError: #No such view
            return None
        
    ## Add an input device (eg; mouse, keyboard, etc) by name if it's not already addded.
    #  \param name Unique identifier of device (usually the plugin name)
    #  \param view The input device to be added
    def addInputDevice(self, name, device):
        if(name not in self._input_devices):
            self._input_devices[name] = device
    
    ## Request input device by name. Returns None if no device is found.
    #  \param name Unique identifier of input device (usually the plugin name)
    #  \return input device if name was found, none otherwise.
    def getInputDevice(self, name):
        try:
            return self._input_devices[name]
        except KeyError: #No such tool
            return None
    
    ## Request tool by name. Returns None if no view is found.
    #  \param name Unique identifier of tool (usually the plugin name)
    #  \return tool if name was found, none otherwise.
    def getTool(self, name):
        try:
            return self._tools[name]
        except KeyError: #No such tool
            return None
    
    ## Add an Tool (transform object, translate object) by name if it's not already addded.
    #  \param name Unique identifier of tool (usually the plugin name)
    #  \param tool Tool to be added
    #  \return Tool if name was found, None otherwise.    
    def addTool(self, name, tool):
        if(name not in self._tools):
            self._tools[name] = tool
    
    ## Request active tool. Returns None if there is no active tool
    #  \return Tool if an tool is active, None otherwise.
    def getActiveTool(self):
        return self._active_tool
    
    ## Request active view. Returns None if there is no active view
    #  \return Tool if an view is active, None otherwise.
    def getActiveView(self):
        return self._active_view

    ##  Set the currently active view.
    #   \parma name The name of the view to set as active
    def setActiveView(self, name):
        try:
            self._active_view = self._views[name]
        except KeyError:
            pass

