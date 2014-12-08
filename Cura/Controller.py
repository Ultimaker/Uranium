from Cura.InputDevice import InputDevice
from Cura.View.View import View
from Cura.Tool import Tool
from Cura.Scene.Scene import Scene
from Cura.Event import Event, MouseEvent, ToolEvent
from Cura.Math.Vector import Vector
from Cura.Math.Quaternion import Quaternion
from Cura.Signal import Signal, SignalEmitter

## Glue glass that holds the scene, (active) view(s), (active) tool(s) and possible user inputs.
#
#  The different types of views / tools / inputs are defined by plugins.
class Controller(SignalEmitter):
    def __init__(self, application):
        super().__init__() # Call super to make multiple inheritence work.
        self._active_tool = None
        self._tools = {}
        
        self._input_devices = {}
        
        self._active_view = None
        self._views = {}
        self._scene = Scene()
        self._application = application
    
    ##  Get the application.
    #   \returns Application
    def getApplication(self):
        return self._application
    
    ##  Add a view by name if it's not already added.
    #   \param name Unique identifier of view (usually the plugin name)
    #   \param view The view to be added
    def addView(self, name, view):
        if(name not in self._views):
            self._views[name] = view
            view.setController(self)
            view.setRenderer(self._application.getRenderer())
            self.viewsChanged.emit()
        else:
            self._application.log('w', '%s was already added to view list. Unable to add it again.',name)
    
    ##  Request view by name. Returns None if no view is found.
    #   \param name Unique identifier of view (usually the plugin name)
    #   \return View if name was found, none otherwise.
    def getView(self, name):
        try:
            return self._views[name]
        except KeyError: #No such view
            self._application.log('e', "Unable to find %s in view list",name)
            return None

    ##  Return all views.
    def getAllViews(self):
        return self._views

    ## Request active view. Returns None if there is no active view
    #  \return Tool if an view is active, None otherwise.
    def getActiveView(self):
        return self._active_view

    ##  Set the currently active view.
    #   \parma name The name of the view to set as active
    def setActiveView(self, name):
        try:
            self._active_view = self._views[name]
            self.activeViewChanged.emit()
        except KeyError:
            self._application.log('e', "No view named %s found", name)

    ##  Emitted when the list of views changes.
    viewsChanged = Signal()

    ##  Emitted when the active view changes.
    activeViewChanged = Signal()
        
    ##  Add an input device (eg; mouse, keyboard, etc) by name if it's not already addded.
    #   \param name Unique identifier of device (usually the plugin name)
    #   \param view The input device to be added
    def addInputDevice(self, name, device):
        if(name not in self._input_devices):
            self._input_devices[name] = device
            device.event.connect(self.event)
        else:
            self._application.log('w', '%s was already added to input device list. Unable to add it again.', name)
    
    ##  Request input device by name. Returns None if no device is found.
    #   \param name Unique identifier of input device (usually the plugin name)
    #   \return input device if name was found, none otherwise.
    def getInputDevice(self, name):
        try:
            return self._input_devices[name]
        except KeyError: #No such tool
            self._application.log('e', "Unable to find %s in input devices",name)
            return None

    ##  Remove an input device from the list of input devices.
    #   Does nothing if the input device is not in the list.
    #   \param name The name of the device to remove.
    def removeInputDevice(self, name):
        if name in self._input_devices:
            self._input_devices[name].event.disconnect(self.event)
            del self._input_devices[name]
    
    ##  Request tool by name. Returns None if no view is found.
    #   \param name Unique identifier of tool (usually the plugin name)
    #   \return tool if name was found, none otherwise.
    def getTool(self, name):
        try:
            return self._tools[name]
        except KeyError: #No such tool
            self._application.log('e', "Unable to find %s in tools",name)
            return None
    
    def getAllTools(self):
        return self._tools

    ##  Add an Tool (transform object, translate object) by name if it's not already addded.
    #   \param name Unique identifier of tool (usually the plugin name)
    #   \param tool Tool to be added
    #   \return Tool if name was found, None otherwise.    
    def addTool(self, name, tool):
        if(name not in self._tools):
            self._tools[name] = tool
            self.toolsChanged.emit()
        else: 
            self._application.log('w', '%s was already added to tool list. Unable to add it again.', name)
    
    ## Request active tool. Returns None if there is no active tool
    #  \return Tool if an tool is active, None otherwise.
    def getActiveTool(self):
        return self._active_tool

    ##  Set the current active tool.
    #   \param name The name of the tool to set as active.
    def setActiveTool(self, name):
        try:
            if self._active_tool:
                self._active_tool.event(ToolEvent(ToolEvent.ToolDeactivateEvent))

            self._active_tool = self._tools[name]

            if self._active_tool:
                self._active_tool.event(ToolEvent(ToolEvent.ToolActivateEvent))

            self.activeToolChanged.emit()
        except KeyError:
            self._application.log('e', 'No tool named %s found.', name)

    ##  Emitted when the list of tools changes.
    toolsChanged = Signal()

    ##  Emitted when the active tool changes.
    activeToolChanged = Signal()

    ##  Return the scene
    def getScene(self):
        return self._scene

    ## Process an event
    def event(self, event):
        # First, try to perform camera control
        if type(event) is MouseEvent:
            if MouseEvent.RightButton in event.buttons:
                self._rotateCamera(event)
                return
            elif MouseEvent.MiddleButton in event.buttons:
                self._moveCamera(event)
                return
        elif event.type is Event.MouseWheelEvent:
            self._zoomCamera(event)

        # If we are not doing camera control, pass the event to the active tool.
        if self._active_tool and self._active_tool.event(event):
            return

        #TODO: Handle selection

    ##  private:

    #   Moves the camera in response to a mouse event.
    def _moveCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        camera.translate(Vector(event.deltaX / 100.0, event.deltaY / 100.0, 0))

    #   Zooms the camera in response to a mouse event.
    def _zoomCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        camera.translate(Vector(0.0, 0.0, -event.vertical / 10.0))

    #   Rotates the camera in response to a mouse event.
    def _rotateCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        camera.rotateByAngleAxis(event.deltaX / 10.0, Vector(0, 1, 0))
        camera.rotateByAngleAxis(event.deltaY / 10.0, Vector(1, 0, 0))

