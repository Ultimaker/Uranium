from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Application import Application
class PointCloudAlignTool(Tool):
    def __init__(self):
        super().__init__()
        self._previous_view = ""
        
        
    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            #Activate the right view
            self._previous_view = Application.getInstance().getController().getActiveView().getPluginId()
            Application.getInstance().getController().setActiveView("PointCloudAlign")
            
        if event.type == Event.ToolDeactivateEvent:
            Application.getInstance().getController().setActiveView(self._previous_view)
            