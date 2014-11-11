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

    def getActiveTool(self):
        return self._active_tool
    
    def getActiveView(self):
        return self._active_view
