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


@signalemitter
class Controller:
    """Glue class that holds the scene, (active) view(s), (active) tool(s) and possible user inputs.

    The different types of views / tools / inputs are defined by plugins.
    :sa View
    :sa Tool
    :sa Scene
    """

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

    def addView(self, view: View) -> None:
        """Add a view by name if it"s not already added.

        :param view: The view to be added
        """

        name = view.getId()
        if name not in self._views:
            self._views[name] = view
            view.setRenderer(self._application.getRenderer())
            self.viewsChanged.emit()
        else:
            Logger.log("w", "%s was already added to view list. Unable to add it again.", name)

    def getView(self, name: str) -> Optional[View]:
        """Request view by name. Returns None if no view is found.

        :return: View  if name was found, none otherwise.
        """

        try:
            return self._views[name]
        except KeyError:  # No such view
            Logger.log("e", "Unable to find %s in view list", name)
            return None

    def getAllViews(self) -> Dict[str, View]:
        """Return all views.

        :return: views
        """

        return self._views

    def getActiveView(self) -> Optional[View]:
        """Request active view. Returns None if there is no active view

        :return: view if an view is active, None otherwise.
        """

        return self._active_view

    def setActiveView(self, name: str) -> None:
        """Set the currently active view.

        :param name:  The name of the view to set as active
        """

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

    viewsChanged = Signal()
    """Emitted when the list of views changes."""

    activeViewChanged = Signal()
    """Emitted when the active view changes."""

    def addStage(self, stage: Stage) -> None:
        """Add a stage if it's not already added.

        :param stage: The stage to be added
        """

        name = stage.getId()
        if name not in self._stages:
            self._stages[name] = stage
            self.stagesChanged.emit()

    def getStage(self, name: str) -> Optional[Stage]:
        """Request stage by name. Returns None if no stage is found.

        :param name: Unique identifier of stage (usually the plugin name)
        :return: Stage if name was found, None otherwise.
        """

        try:
            return self._stages[name]
        except KeyError:  # No such view
            Logger.log("e", "Unable to find %s in stage list", name)
            return None

    def getAllStages(self) -> Dict[str, Stage]:
        """Return all stages.

        :return: stages
        """

        return self._stages

    def getActiveStage(self) -> Optional[Stage]:
        """Request active stage. Returns None if there is no active stage

        :return: stage if an stage is active, None otherwise.
        """

        return self._active_stage

    def setActiveStage(self, name: str) -> None:
        """Set the currently active stage.

        :param name: The name of the stage to set as active
        """

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

    stagesChanged = Signal()
    """Emitted when the list of stages changes."""

    activeStageChanged = Signal()
    """Emitted when the active stage changes."""

    def addInputDevice(self, device: InputDevice) -> None:
        """Add an input device (e.g. mouse, keyboard, etc) if it's not already added.

        :param device: The input device to be added
        """

        name = device.getId()
        if name not in self._input_devices:
            self._input_devices[name] = device
            device.event.connect(self.event)
        else:
            Logger.log("w", "%s was already added to input device list. Unable to add it again." % name)

    def getInputDevice(self, name: str) -> Optional[InputDevice]:
        """Request input device by name. Returns None if no device is found.

        :param name: Unique identifier of input device (usually the plugin name)
        :return: input device if name was found, none otherwise.
        """

        try:
            return self._input_devices[name]
        except KeyError:  # No such device
            Logger.log("e", "Unable to find %s in input devices", name)
            return None

    def removeInputDevice(self, name: str) -> None:
        """Remove an input device from the list of input devices.

        Does nothing if the input device is not in the list.
        :param name: The name of the device to remove.
        """

        if name in self._input_devices:
            self._input_devices[name].event.disconnect(self.event)
            del self._input_devices[name]

    def getFallbackTool(self) -> str:
        """Request the current fallbacl tool.

        :return: Id of the fallback tool
        """

        return self._fallback_tool

    def setFallbackTool(self, tool: str) -> None:
        """Set the current active tool. The tool must be set by name.

        :param tool: The tools name which shall be used as fallback
        """

        if self._fallback_tool is not tool:
            self._fallback_tool = tool

    def getTool(self, name: str) -> Optional["Tool"]:
        """Request tool by name. Returns None if no tool is found.

        :param name: Unique identifier of tool (usually the plugin name)
        :return: tool if name was found, None otherwise.
        """

        try:
            return self._tools[name]
        except KeyError:  # No such tool
            Logger.log("e", "Unable to find %s in tools", name)
            return None

    def getAllTools(self) -> Dict[str, "Tool"]:
        """Get all tools

        :return: tools
        """

        return self._tools

    def addTool(self, tool: "Tool") -> None:
        """Add a Tool (transform object, translate object) if its not already added.

        :param tool: Tool to be added
        """

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

    def isToolOperationActive(self) -> bool:
        """Gets whether a tool is currently in use

        :return: true if a tool current being used.
        """

        return self._tool_operation_active

    def getActiveTool(self) -> Optional["Tool"]:
        """Request active tool. Returns None if there is no active tool

        :return: Tool if a tool is active, None otherwise.
        """

        return self._active_tool

    def setActiveTool(self, tool: Optional[Union["Tool", str]]):
        """Set the current active tool.

        The tool can be set by name of the tool or directly passing the tool object.
        :param tool: A tool object or the name of a tool.
        """

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

    toolsChanged = Signal()
    """Emitted when the list of tools changes."""

    toolEnabledChanged = Signal()
    """Emitted when a tool changes its enabled state."""

    activeToolChanged = Signal()
    """Emitted when the active tool changes."""

    toolOperationStarted = Signal()
    """Emitted whenever a tool starts a longer operation.

    :param tool: The tool that started the operation.
    :sa Tool::startOperation
    """

    toolOperationStopped = Signal()
    """Emitted whenever a tool stops a longer operation.

    :param tool: The tool that stopped the operation.
    :sa Tool::stopOperation
    """

    def getScene(self) -> Scene:
        """Get the scene

        :return: scene
        """

        return self._scene

    def event(self, event: Event):
        """Process an event

        The event is first passed to the selection tool, then the active tool and finally the camera tool.
        If none of these events handle it (when they return something that does not evaluate to true)
        a context menu signal is emitted.

        :param event: event to be handle.
        """

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

    def setCameraTool(self, tool: Union["Tool", str]):
        """Set the tool used for handling camera controls.

        Camera tool is the first tool to receive events.
        The tool can be set by name of the tool or directly passing the tool object.
        :param tool:
        :sa setSelectionTool
        :sa setActiveTool
        """

        from UM.Tool import Tool
        if isinstance(tool, Tool) or tool is None:
            self._camera_tool = cast(Optional[Tool], tool)
        else:
            self._camera_tool = self.getTool(tool)

    def getCameraTool(self) -> Optional["Tool"]:
        """Get the camera tool (if any)

        :returns: camera tool (or none)
        """

        return self._camera_tool

    def setSelectionTool(self, tool: Union[str, "Tool"]):
        """Set the tool used for performing selections.

        Selection tool receives its events after camera tool and active tool.
        The tool can be set by name of the tool or directly passing the tool object.
        :param tool:
        :sa setCameraTool
        :sa setActiveTool
        """

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

    # Position camera view according to defined position
    def setCameraPosition(self, x_position: int = 0, y_position: int = 0, z_position: int = 0) -> None:
        camera = self._scene.getActiveCamera()
        if not camera:
            return
        camera.setPosition(Vector(x_position, y_position, z_position))

    # Indicate position where the camera should point at
    def setLookAtPosition(self, x_look_at_position: int = 0, y_look_at_position: int = 0, z_look_at_position: int = 0) -> None:
        camera = self._scene.getActiveCamera()
        if not camera:
            return
        camera.lookAt(Vector(x_look_at_position, y_look_at_position, z_look_at_position))

    # Sets the zoom factor of the camera
    def setCameraZoomFactor(self, camera_zoom_factor: float = 0) -> None:
        camera = self._scene.getActiveCamera()
        if not camera:
            return
        camera.setZoomFactor(camera_zoom_factor)

    def setCameraOrigin(self, coordinate: str = "home"):
        """Changes the origin of the camera, i.e. where it looks at.

        :param coordinate: One of the following options:
        - "home": The centre of the build plate.
        - "3d": The centre of the build volume.
        - "x", "y" and "z": Also the centre of the build plate. These are just
        aliases for the setCameraRotation function.
        """

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
