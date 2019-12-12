# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.Scene import Scene
from UM.Event import Event, KeyEvent, MouseEvent, ToolEvent, ViewEvent
from UM.Scene.SceneNode import SceneNode
from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

# Type hinting imports
from UM.View.View import View
from UM.Stage import Stage
from UM.InputDevice import InputDevice
from typing import cast, Optional, Dict, Union
from UM.Math.Vector import Vector
MYPY = False
if MYPY:
    from UM.Application import Application
    from UM.Tool import Tool


##  Glue class that holds the scene, (active) view(s), (active) tool(s) and possible user inputs.
#
#   The different types of views / tools / inputs are defined by plugins.
#   \sa View
#   \sa Tool
#   \sa Scene
@signalemitter
class Controller:
    def __init__(self, application: "Application") -> None:
        super().__init__()  # Call super to make multiple inheritance work.

        self._scene = Scene()
        self._application = application

        self._active_view = None  # type: Optional[View]
        self._views = {}  # type: Dict[str, View]

        self._active_tool = None  # type: Optional[Tool]
        self._fallback_tool = "TranslateTool"  # type: str
        self._tool_operation_active = False
        self._tools = {}  # type: Dict[str, Tool]
        self._camera_tool = None #type: Optional[Tool]
        self._selection_tool = None #type: Optional[Tool]
        self._tools_enabled = True #type: bool

        self._active_stage = None #type: Optional[Stage]
        self._stages = {} #type: Dict[str, Stage]

        self._input_devices = {} #type: Dict[str, InputDevice]

        PluginRegistry.addType("stage", self.addStage)
        PluginRegistry.addType("view", self.addView)
        PluginRegistry.addType("tool", self.addTool)
        PluginRegistry.addType("input_device", self.addInputDevice)

    ##  Add a view by name if it"s not already added.
    #   \param view \type{View} The view to be added
    def addView(self, view: View) -> None:
        name = view.getId()
        if name not in self._views:
            self._views[name] = view
            view.setRenderer(self._application.getRenderer())
            self.viewsChanged.emit()
        else:
            Logger.log("w", "%s was already added to view list. Unable to add it again.", name)

    ##  Request view by name. Returns None if no view is found.
    #   \return View \type{View} if name was found, none otherwise.
    def getView(self, name: str) -> Optional[View]:
        try:
            return self._views[name]
        except KeyError:  # No such view
            Logger.log("e", "Unable to find %s in view list", name)
            return None

    ##  Return all views.
    #   \return views \type{dict}
    def getAllViews(self) -> Dict[str, View]:
        return self._views

    ##  Request active view. Returns None if there is no active view
    #   \return view \type{View} if an view is active, None otherwise.
    def getActiveView(self) -> Optional[View]:
        return self._active_view

    ##  Set the currently active view.
    #   \param name \type{string} The name of the view to set as active
    def setActiveView(self, name: str) -> None:
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
            Logger.logException("e", "An exception occurred while switching views: %s", str(e))

    ##  Emitted when the list of views changes.
    viewsChanged = Signal()

    ##  Emitted when the active view changes.
    activeViewChanged = Signal()

    ##  Add a stage by name if it's not already added.
    #   \param name \type{string} Unique identifier of stage (usually the plugin name)
    #   \param stage \type{Stage} The stage to be added
    def addStage(self, stage: Stage) -> None:
        name = stage.getId()
        if name not in self._stages:
            self._stages[name] = stage
            self.stagesChanged.emit()

    ##  Request stage by name. Returns None if no stage is found.
    #   \param name \type{string} Unique identifier of stage (usually the plugin name)
    #   \return Stage \type{Stage} if name was found, none otherwise.
    def getStage(self, name: str) -> Optional[Stage]:
        try:
            return self._stages[name]
        except KeyError:  # No such view
            Logger.log("e", "Unable to find %s in stage list", name)
            return None

    ##  Return all stages.
    #   \return stages \type{dict}
    def getAllStages(self) -> Dict[str, Stage]:
        return self._stages

    ##  Request active stage. Returns None if there is no active stage
    #   \return stage \type{Stage} if an stage is active, None otherwise.
    def getActiveStage(self) -> Optional[Stage]:
        return self._active_stage

    ##  Set the currently active stage.
    #   \param name \type{string} The name of the stage to set as active
    def setActiveStage(self, name: str) -> None:
        try:
            # Don't actually change the stage if it is the current selected one.
            if self._active_stage != self._stages[name]:
                previous_stage = self._active_stage
                Logger.log("d", "Setting active stage to %s", name)
                self._active_stage = self._stages[name]

                # If there is no error switching stages, then finish first the previous stage (if it exists) and start the new stage
                if previous_stage is not None:
                    previous_stage.onStageDeselected()
                self._active_stage.onStageSelected()
                self.activeStageChanged.emit()
        except KeyError:
            Logger.log("e", "No stage named %s found", name)
        except Exception as e:
            Logger.logException("e", "An exception occurred while switching stages: %s", str(e))

    ##  Emitted when the list of stages changes.
    stagesChanged = Signal()

    ##  Emitted when the active stage changes.
    activeStageChanged = Signal()

    ##  Add an input device (e.g. mouse, keyboard, etc) if it's not already added.
    #   \param device The input device to be added
    def addInputDevice(self, device: InputDevice) -> None:
        name = device.getId()
        if name not in self._input_devices:
            self._input_devices[name] = device
            device.event.connect(self.event)
        else:
            Logger.log("w", "%s was already added to input device list. Unable to add it again." % name)

    ##  Request input device by name. Returns None if no device is found.
    #   \param name \type{string} Unique identifier of input device (usually the plugin name)
    #   \return input \type{InputDevice} device if name was found, none otherwise.
    def getInputDevice(self, name: str) -> Optional[InputDevice]:
        try:
            return self._input_devices[name]
        except KeyError:  # No such device
            Logger.log("e", "Unable to find %s in input devices", name)
            return None

    ##  Remove an input device from the list of input devices.
    #   Does nothing if the input device is not in the list.
    #   \param name \type{string} The name of the device to remove.
    def removeInputDevice(self, name: str) -> None:
        if name in self._input_devices:
            self._input_devices[name].event.disconnect(self.event)
            del self._input_devices[name]

    ##  Request the current fallbacl tool.
    #   \return Id of the fallback tool
    def getFallbackTool(self) -> str:
        return self._fallback_tool

    ##  Set the current active tool. The tool must be set by name.
    #   \param tool The tools name which shall be used as fallback
    def setFallbackTool(self, tool: str) -> None:
        if self._fallback_tool is not tool:
            self._fallback_tool = tool

    ##  Request tool by name. Returns None if no tool is found.
    #   \param name \type{string} Unique identifier of tool (usually the plugin name)
    #   \return tool \type{Tool} if name was found, None otherwise.
    def getTool(self, name: str) -> Optional["Tool"]:
        try:
            return self._tools[name]
        except KeyError:  # No such tool
            Logger.log("e", "Unable to find %s in tools", name)
            return None

    ##  Get all tools
    #   \return tools \type{dict}
    def getAllTools(self) -> Dict[str, "Tool"]:
        return self._tools

    ##  Add a Tool (transform object, translate object) if its not already added.
    #   \param tool \type{Tool} Tool to be added
    def addTool(self, tool: "Tool") -> None:
        name = tool.getId()
        if name not in self._tools:
            self._tools[name] = tool
            tool.operationStarted.connect(self._onToolOperationStarted)
            tool.operationStopped.connect(self._onToolOperationStopped)
            self.toolsChanged.emit()
        else:
            Logger.log("w", "%s was already added to tool list. Unable to add it again.", name)

    def _onToolOperationStarted(self, tool: "Tool") -> None:
        if not self._tool_operation_active:
            self._tool_operation_active = True
            self.toolOperationStarted.emit(tool)

    def _onToolOperationStopped(self, tool: "Tool") -> None:
        if self._tool_operation_active:
            self._tool_operation_active = False
            self.toolOperationStopped.emit(tool)

    ##  Gets whether a tool is currently in use
    #   \return \type{bool} true if a tool current being used.
    def isToolOperationActive(self) -> bool:
        return self._tool_operation_active

    ##  Request active tool. Returns None if there is no active tool
    #   \return Tool if a tool is active, None otherwise.
    def getActiveTool(self) -> Optional["Tool"]:
        return self._active_tool

    ##  Set the current active tool.
    #   The tool can be set by name of the tool or directly passing the tool object.
    #   \param tool A tool object or the name of a tool.
    def setActiveTool(self, tool: Optional[Union["Tool", str]]):
        from UM.Tool import Tool
        if self._active_tool:
            self._active_tool.event(ToolEvent(ToolEvent.ToolDeactivateEvent))

        if isinstance(tool, Tool) or tool is None:
            new_tool = cast(Optional[Tool], tool)
        else:
            new_tool = self.getTool(tool)

        tool_changed = False
        if self._active_tool is not new_tool:
            self._active_tool = new_tool
            tool_changed = True

        if self._active_tool:
            self._active_tool.event(ToolEvent(ToolEvent.ToolActivateEvent))

        from UM.Scene.Selection import Selection  # Imported here to prevent a circular dependency.
        if not self._active_tool and Selection.getCount() > 0:  # If something is selected, a tool must always be active.
            if self._fallback_tool in self._tools:
                self._active_tool = self._tools[self._fallback_tool]  # Then default to the translation tool.
                self._active_tool.event(ToolEvent(ToolEvent.ToolActivateEvent))
                tool_changed = True
            else:
                Logger.log("w", "Controller does not have an active tool and could not default to the tool, called \"{}\".".format(self._fallback_tool))

        if tool_changed:
            Selection.setFaceSelectMode(False)
            Selection.clearFace()
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
    def getScene(self) -> Scene:
        return self._scene

    ##  Process an event
    #   \param event \type{Event} event to be handle.
    #   The event is first passed to the selection tool, then the active tool and finally the camera tool.
    #   If none of these events handle it (when they return something that does not evaluate to true)
    #   a context menu signal is emitted.
    def event(self, event: Event):
        if self._selection_tool and self._selection_tool.event(event):
            return

        if self._active_tool and self._active_tool.event(event):
            return

        if self._camera_tool and self._camera_tool.event(event):
            return

        if self._tools and event.type == Event.KeyPressEvent:
            event = cast(KeyEvent, event)
            from UM.Scene.Selection import Selection  # Imported here to prevent a circular dependency.
            if Selection.hasSelection():
                for key, tool in self._tools.items():
                    if tool.getShortcutKey() is not None and event.key == tool.getShortcutKey():
                        self.setActiveTool(tool)

        if self._active_view:
            self._active_view.event(event)

        if event.type == Event.MouseReleaseEvent:
            event = cast(MouseEvent, event)
            if MouseEvent.RightButton in event.buttons:
                self.contextMenuRequested.emit(event.x, event.y)

    contextMenuRequested = Signal()

    ##  Set the tool used for handling camera controls.
    #   Camera tool is the first tool to receive events.
    #   The tool can be set by name of the tool or directly passing the tool object.
    #   \param tool \type{Tool} or \type{string}
    #   \sa setSelectionTool
    #   \sa setActiveTool
    def setCameraTool(self, tool: Union["Tool", str]):
        from UM.Tool import Tool
        if isinstance(tool, Tool) or tool is None:
            self._camera_tool = cast(Optional[Tool], tool)
        else:
            self._camera_tool = self.getTool(tool)

    ##  Get the camera tool (if any)
    #   \returns camera tool (or none)
    def getCameraTool(self) -> Optional["Tool"]:
        return self._camera_tool

    ##  Set the tool used for performing selections.
    #   Selection tool receives its events after camera tool and active tool.
    #   The tool can be set by name of the tool or directly passing the tool object.
    #   \param tool \type{Tool} or \type{string}
    #   \sa setCameraTool
    #   \sa setActiveTool
    def setSelectionTool(self, tool: Union[str, "Tool"]):
        from UM.Tool import Tool
        if isinstance(tool, Tool) or tool is None:
            self._selection_tool = cast(Optional[Tool], tool)
        else:
            self._selection_tool = self.getTool(tool)

    def getToolsEnabled(self) -> bool:
        return self._tools_enabled

    def setToolsEnabled(self, enabled: bool) -> None:
        self._tools_enabled = enabled

    def deleteAllNodesWithMeshData(self, only_selectable:bool = True) -> None:
        Logger.log("i", "Clearing scene")
        if not self.getToolsEnabled():
            return

        nodes = []
        for node in DepthFirstIterator(self.getScene().getRoot()):
            if not node.isEnabled():
                continue
            if not node.getMeshData() and not node.callDecoration("isGroup"):
                continue  # Node that doesnt have a mesh and is not a group.
            if only_selectable and not node.isSelectable():
                continue  # Only remove nodes that are selectable.
            if node.getParent() and cast(SceneNode, node.getParent()).callDecoration("isGroup"):
                continue  # Grouped nodes don't need resetting as their parent (the group) is resetted)
            nodes.append(node)
        if nodes:
            from UM.Operations.GroupedOperation import GroupedOperation
            op = GroupedOperation()

            for node in nodes:
                from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
                op.addOperation(RemoveSceneNodeOperation(node))

                # Reset the print information
                self.getScene().sceneChanged.emit(node)

            op.push()
            from UM.Scene.Selection import Selection
            Selection.clear()

    # Rotate camera view according defined angle
    def setCameraRotation(self, coordinate: str = "x", angle: int = 0) -> None:
        camera = self._scene.getActiveCamera()
        if not camera:
            return
        camera.setZoomFactor(camera.getDefaultZoomFactor())
        self._camera_tool.setOrigin(Vector(0, 100, 0))  # type: ignore
        self.setCameraOrigin(coordinate)
        if coordinate == "home":
            camera.setPosition(Vector(0, 100, 700))
            self._camera_tool.rotateCamera(0, 0)  # type: ignore
        elif coordinate == "3d":
            camera.setPosition(Vector(-750, 600, 700))
            self._camera_tool.rotateCamera(0, 0)  # type: ignore
        else:
            # for comparison is == used, because might not store them at the same location
            # https://stackoverflow.com/questions/1504717/why-does-comparing-strings-in-python-using-either-or-is-sometimes-produce

            if coordinate == "x":
                camera.setPosition(Vector(0, 100, 700))
                self._camera_tool.rotateCamera(angle, 0)  # type: ignore
            elif coordinate == "y":
                if angle == 90:
                    # Prepare the camera for top view, so no rotation has to be applied after setting the top view.
                    camera.setPosition(Vector(0, 100, 100))
                    self._camera_tool.rotateCamera(90, 0)  # type: ignore
                    # Actually set the top view.
                    camera.setPosition(Vector(0, 800, 1))
                    self.setCameraOrigin("z")
                    camera.lookAt(Vector(0, 100, 1))
                    self._camera_tool.rotateCamera(0, 0)  # type: ignore
                else:
                    camera.setPosition(Vector(0, 100, 700))
                    self._camera_tool.rotateCamera(0, angle)  # type: ignore

    ##  Changes the origin of the camera, i.e. where it looks at.
    #   \param coordinate One of the following options:
    #    - "home": The centre of the build plate.
    #    - "3d": The centre of the build volume.
    #    - "x", "y" and "z": Also the centre of the build plate. These are just
    #      aliases for the setCameraRotation function.
    def setCameraOrigin(self, coordinate: str = "home"):
        camera = self._scene.getActiveCamera()
        if not camera:
            return
        coordinates = {
            "home": Vector(0, 100, 0),
            "3d": Vector(0, 100, 100),
            "x": Vector(0, 100, 0),
            "y": Vector(0, 100, 0),
            "z": Vector(0, 100, 1)
        }
        camera.lookAt(coordinates[coordinate])
