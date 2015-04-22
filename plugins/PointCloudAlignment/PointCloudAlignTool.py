from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Application import Application
class PointCloudAlignTool(Tool):
    def __init__(self):
        super().__init__()
        self._previous_view = ""
        self._renderer = Application.getInstance().getRenderer()
        # Were aligning two cloud sets with eachother by slecting points that are the same
        self._vert_list_1 = []
        self._vert_list_2 = []
        
    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            self._vert_list_1 = []
            self._vert_list_2 = []
            #Activate the right view
            self._previous_view = Application.getInstance().getController().getActiveView().getPluginId()
            Application.getInstance().getController().setActiveView("PointCloudAlignment")
            
        if event.type == Event.ToolDeactivateEvent:
            Application.getInstance().getController().setActiveView(self._previous_view)
            
        if event.type == MouseEvent.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            pixel_color = self._renderer.getSelectionColorAtCoordinate(event.x,event.y)
            if pixel_color:
                if pixel_color.a:
                    index  = int(255 - pixel_color.a * 255)
                    targeted_node = Application.getInstance().getCloudNodeByIndex(index)
                    pixel_index = int(pixel_color.r * 255) + (int(pixel_color.g * 255) << 8) + (int(pixel_color.b * 255) << 16)
                    temp = targeted_node.getMeshData().getVertex(pixel_index)
                    print(temp)