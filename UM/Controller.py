# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.Scene import Scene
from UM.Event import Event, MouseEvent, ToolEvent, ViewEvent
from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry


##      Glue class that holds the scene, (active) view(s), (active) tool(s) and possible user inputs.
#
#       The different types of views / tools / inputs are defined by plugins.
#       \sa View
#       \sa Tool
#       \sa Scene
@signalemitter
class Controller:
    def __init__(self, application):
        super().__init__()  # Call super to make multiple inheritance work.
        self._active_tool = None
        self._tool_operation_active = False
        self._tools = {}

        self._input_devices = {}

        self._active_view = None
        self._views = {}
        self._scene = Scene()
        self._application = application
        self._camera_tool = None
        self._selection_tool = None

        self._tools_enabled = True

        PluginRegistry.addType("view", self.addView)
        PluginRegistry.addType("tool", self.addTool)
        PluginRegistry.addType("input_device", self.addInputDevice)

    ##  Get the application.
    #   \returns Application \type {Application}
    def getApplication(self):
        return self._application

    ##  Add a view by name if it"s not already added.
    #   \param name \type{string} Unique identifier of view (usually the plugin name)
    #   \param view \type{View} The view to be added
    def addView(self, view):
        name = view.getPluginId()
        if name not in self._views:
            self._views[name] = view
            #view.setController(self)
            view.setRenderer(self._application.getRenderer())
            self.viewsChanged.emit()
        else:
            Logger.log("w", "%s was already added to view list. Unable to add it again.", name)

    ##  Request view by name. Returns None if no view is found.
    #   \param name \type{string} Unique identifier of view (usually the plugin name)
    #   \return View \type{View} if name was found, none otherwise.
    def getView(self, name):
        try:
            return self._views[name]
        except KeyError:  # No such view
            Logger.log("e", "Unable to find %s in view list", name)
            return None

    ##  Return all views.
    #   \return views \type{list}
    def getAllViews(self):
        return self._views

    ##  Request active view. Returns None if there is no active view
    #   \return view \type{View} if an view is active, None otherwise.
    def getActiveView(self):
        return self._active_view

    ##  Set the currently active view.
    #   \param name \type{string} The name of the view to set as active
    def setActiveView(self, name):
        Logger.log("d", "Setting active view to %s", name)
        try:
            if self._active_view:
                self._active_view.event(ViewEvent(Event.ViewDeactivateEvent))

            self._active_view = self._views[name]

            if self._active_view:
                self._active_view.event(ViewEvent(Event.ViewActivateEvent))

            self.activeViewChanged.emit()
        except KeyError:
            Logger.log("e", "No view named %s found", name)
        except Exception as e:
            Logger.log("e", "An exception occurred while switching views", str(e))

    ##  Emitted when the list of views changes.
    viewsChanged = Signal()

    ##  Emitted when the active view changes.
    activeViewChanged = Signal()

    ##  Add an input device (e.g. mouse, keyboard, etc) if it's not already added.
    #   \param device The input device to be added
    def addInputDevice(self, device):
        name = device.getPluginId()
        if name not in self._input_devices:
            self._input_devices[name] = device
            device.event.connect(self.event)
        else:
            Logger.log("w", "%s was already added to input device list. Unable to add it again." % name)

    ##  Request input device by name. Returns None if no device is found.
    #   \param name \type{string} Unique identifier of input device (usually the plugin name)
    #   \return input \type{InputDevice} device if name was found, none otherwise.
    def getInputDevice(self, name):
        try:
            return self._input_devices[name]
        except KeyError: #No such device
            Logger.log("e", "Unable to find %s in input devices", name)
            return None

    ##  Remove an input device from the list of input devices.
    #   Does nothing if the input device is not in the list.
    #   \param name \type{string} The name of the device to remove.
    def removeInputDevice(self, name):
        if name in self._input_devices:
            self._input_devices[name].event.disconnect(self.event)
            del self._input_devices[name]

    ##  Request tool by name. Returns None if no view is found.
    #   \param name \type{string} Unique identifier of tool (usually the plugin name)
    #   \return tool \type{Tool} if name was found, none otherwise.
    def getTool(self, name):
        try:
            return self._tools[name]
        except KeyError: #No such tool
            Logger.log("e", "Unable to find %s in tools", name)
            return None

    ##  Get all tools
    #   \return tools \type{list}
    def getAllTools(self):
        return self._tools

    ##  Add a Tool (transform object, translate object) if its not already added.
    #   \param tool \type{Tool} Tool to be added
    def addTool(self, tool):
        name = tool.getPluginId()
        if name not in self._tools:
            self._tools[name] = tool
            tool.operationStarted.connect(self._onToolOperationStarted)
            tool.operationStopped.connect(self._onToolOperationStopped)
            self.toolsChanged.emit()
        else:
            Logger.log("w", "%s was already added to tool list. Unable to add it again.", name)

    def _onToolOperationStarted(self, tool):
        self._tool_operation_active = True
        self.toolOperationStarted.emit(tool)

    def _onToolOperationStopped(self, tool):
        self._tool_operation_active = False
        self.toolOperationStopped.emit(tool)

    ##  Gets whether a tool is currently in use
    #   \return \type{bool} true if a tool current being used.
    def isToolOperationActive(self):
        return self._tool_operation_active

    ##  Request active tool. Returns None if there is no active tool
    #   \return Tool \type{Tool} if an tool is active, None otherwise.
    def getActiveTool(self):
        return self._active_tool

    ##  Set the current active tool.
    #   The tool can be set by name of the tool or directly passing the tool object.
    #   \param tool \type{Tool} or \type{string}
    def setActiveTool(self, tool):
        from UM.Tool import Tool
        if self._active_tool:
            self._active_tool.event(ToolEvent(ToolEvent.ToolDeactivateEvent))

        if isinstance(tool, Tool) or tool is None:
            self._active_tool = tool
        else:
            self._active_tool = self.getTool(tool)

        if self._active_tool:
            self._active_tool.event(ToolEvent(ToolEvent.ToolActivateEvent))

        from UM.Scene.Selection import Selection  # Imported here to prevent a circular dependency.
        if not self._active_tool and Selection.getCount() > 0:  # If something is selected, a tool must always be active.
            self._active_tool = self._tools["TranslateTool"]  # Then default to the translation tool.
            self._active_tool.event(ToolEvent(ToolEvent.ToolActivateEvent))

        self.activeToolChanged.emit()

    ##  Emitted when the list of tools changes.
    toolsChanged = Signal()

    ##  Emitted when a tool changes its enabled state.
    toolEnabledChanged = Signal()

    ##  Emitted when the active tool changes.
    activeToolChanged = Signal()

    ##  Emitted whenever a tool starts a longer operation.
    #
    #   \param tool The tool that started the operation.
    #   \sa Tool::startOperation
    toolOperationStarted = Signal()

    ##  Emitted whenever a tool stops a longer operation.
    #
    #   \param tool The tool that stopped the operation.
    #   \sa Tool::stopOperation
    toolOperationStopped = Signal()

    ##  Get the scene
    #   \return scene \type{Scene}
    def getScene(self):
        return self._scene

    ##  Process an event
    #   \param event \type{Event} event to be handle.
    #   The event is first passed to the camera tool, then active tool and finally selection tool.
    #   If none of these events handle it (when they return something that does not evaluate to true)
    #   a context menu signal is emitted.
    def event(self, event):
        # First, try to perform camera control
        if self._camera_tool and self._camera_tool.event(event):
            return

        if self._selection_tool and self._selection_tool.event(event):
            return

        # If we are not doing camera control, pass the event to the active tool.
        if self._active_tool and self._active_tool.event(event):
            return

        if self._active_view:
            self._active_view.event(event)

        if event.type == Event.MouseReleaseEvent and MouseEvent.RightButton in event.buttons:
            self.contextMenuRequested.emit(event.x, event.y)

    contextMenuRequested = Signal()

    ##  Set the tool used for handling camera controls.
    #   Camera tool is the first tool to receive events.
    #   The tool can be set by name of the tool or directly passing the tool object.
    #   \param tool \type{Tool} or \type{string}
    #   \sa setSelectionTool
    #   \sa setActiveTool
    def setCameraTool(self, tool):
        from UM.Tool import Tool
        if isinstance(tool, Tool) or tool is None:
            self._camera_tool = tool
        else:
            self._camera_tool = self.getTool(tool)

    ##  Get the camera tool (if any)
    #   \returns camera tool (or none)
    def getCameraTool(self):
        return self._camera_tool

    ##  Set the tool used for performing selections.
    #   Selection tool receives its events after camera tool and active tool.
    #   The tool can be set by name of the tool or directly passing the tool object.
    #   \param tool \type{Tool} or \type{string}
    #   \sa setCameraTool
    #   \sa setActiveTool
    def setSelectionTool(self, tool):
        from UM.Tool import Tool
        if isinstance(tool, Tool) or tool is None:
            self._selection_tool = tool
        else:
            self._selection_tool = self.getTool(tool)

    def getToolsEnabled(self):
        return self._tools_enabled

    def setToolsEnabled(self, enabled):
        self._tools_enabled = enabled
