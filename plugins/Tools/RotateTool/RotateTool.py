from UM.Tool import Tool
from UM.Event import Event

class RotateTool(Tool):
    def __init__(self):
        super().__init__()

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            print("Activate Rotate tool")

