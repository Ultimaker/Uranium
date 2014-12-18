from UM.Tool import Tool
from UM.Event import Event

class RotateTool(Tool):
    def __init__(self, name):
        super().__init__(name)

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            print("Activate Rotate tool")

    def getIconName(self):
        return 'rotate.png'
