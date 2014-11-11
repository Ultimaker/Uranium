from Cura.InputDevice import InputDevice
from Cura.View.View import View
from Cura.Tool import Tool

class Controller(object):
    def __init__(self):
        self._active_tool = None
        self._tools = {}
        
        self._input_devices = {}
        self._active_view = None
        self._views = {}
        
    def addView(self, name, view):
        self._views[name] = view
    
    def getView(self, name):
        try:
            return self._views[name]
        except KeyError: #No such view
            return None
    
    def getTool(self, name):
        try:
            return self._tools[name]
        except KeyError: #No such tool
            return None
        
    def addTool(self, name, tool):
        self._tools[name] = tool
    

    def getActiveTool(self):
        return self._active_tool
    
    def getActiveView(self):
        return self._active_view
