from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Application import Application
from . import PointCloudAlignToolHandle
from UM.Math.Vector import Vector
class PointCloudAlignTool(Tool):
    def __init__(self):
        super().__init__()
        self._previous_view = ""
        self._renderer = Application.getInstance().getRenderer()
        # Were aligning two cloud sets with eachother by slecting points that are the same
        self._node_1 = None
        self._node_2 = None
        self._vert_list_1 = []
        self._vert_list_2 = []
        self._active_node_nr = 1
        self._handle = PointCloudAlignToolHandle.PointCloudAlignToolHandle()
        
    def setAlignmentNodes(self, node1, node2):
        self._active_node_nr = 1
        self._node_1 = node1
        self._node_2 = node2
        self._node_2.setEnabled(False)
        Application.getInstance().getController().getScene().sceneChanged.emit(self)
        
    def event(self, event):
        
        
        if event.type == Event.ToolActivateEvent:
            self._vert_list_1 = []
            self._vert_list_2 = []
            #Activate the right view
            self._previous_view = Application.getInstance().getController().getActiveView().getPluginId()
            Application.getInstance().getController().setActiveView("PointCloudAlignment")
            self._handle.setParent(Application.getInstance().getController().getScene().getRoot())
            
        if event.type == Event.ToolDeactivateEvent:
            Application.getInstance().getController().setActiveView(self._previous_view)
            
        if event.type == MouseEvent.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            pixel_color = self._renderer.getSelectionColorAtCoordinate(event.x,event.y)
            if pixel_color:
                if pixel_color.a:
                    index  = int(255 - pixel_color.a * 255)
                    targeted_node = Application.getInstance().getCloudNodeByIndex(index)
                    pixel_index = int(pixel_color.r * 255) + (int(pixel_color.g * 255) << 8) + (int(pixel_color.b * 255) << 16)
                    selected_vertex = targeted_node.getMeshData().getVertex(pixel_index)
                    self._handle.addSelectedPoint1(selected_vertex)
                    #self._handle.setPosition(Vector(selected_vertex[0],selected_vertex[1],selected_vertex[2]))
                    self._handle.setPosition(Vector(0,0,0))
                    if self._active_node_nr == 1:
                        self._vert_list_1.append(selected_vertex)
                        self._active_node_nr = 2
                        self._node_1.setEnabled(False)
                        self._node_2.setEnabled(True)
                    else:
                        self._vert_list_2.append(selected_vertex)
                        self._active_node_nr = 1
                        self._node_1.setEnabled(True)
                        self._node_2.setEnabled(False)
                    Application.getInstance().getController().getScene().sceneChanged.emit(self)
                    print(selected_vertex)