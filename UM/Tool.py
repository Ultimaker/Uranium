# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List, Optional, Union, cast

import UM.Application  # Circular dependency blah
from UM.Controller import Controller
from UM.Event import Event, MouseEvent
from UM.Math.Plane import Plane #Typing for drag plane.
from UM.Math.Vector import Vector #Typing for drag coordinates.
from UM.PluginObject import PluginObject
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle
from UM.Signal import Signal, signalemitter
from UM.View.SelectionPass import SelectionPass


@signalemitter
class Tool(PluginObject):
    """Abstract base class for tools that manipulate (or otherwise interact with) the scene."""

    def __init__(self) -> None:
        super().__init__()
        self._controller = UM.Application.Application.getInstance().getController()  # Circular dependency blah
        self._enabled = True

        self._handle: Optional[ToolHandle] = None
        self._locked_axis: int = ToolHandle.NoAxis
        self._drag_plane: Optional[Plane] = None
        self._drag_start: Optional[Vector] = None
        self._exposed_properties: List[str] = []

        self._selection_pass: Optional[SelectionPass] = None

        self._controller.toolEnabledChanged.connect(self._onToolEnabledChanged)
        Selection.selectionChanged.connect(self._onSelectionChanged)
        self._selected_objects_without_selected_ancestors: Optional[List[SceneNode]] = None

        self._shortcut_key: Optional[int] = None
        self._active_view: Optional[str] = None

    operationStarted = Signal()
    """Should be emitted whenever a longer running operation is started, like a drag to scale an object.

    :param tool: The tool that started the operation.
    """

    operationStopped = Signal()
    """Should be emitted whenever a longer running operation is stopped.

    :param tool: The tool that stopped the operation.
    """

    propertyChanged = Signal()

    activeViewChanged = Signal()

    def getExposedProperties(self) -> List[str]:
        return self._exposed_properties

    def setExposedProperties(self, *args: str):
        self._exposed_properties = list(args)

    def getShortcutKey(self) -> Optional[int]:
        return self._shortcut_key

    def getActiveView(self) -> Optional[str]:
        return self._active_view

    def setActiveView(self, name: str) -> None:
        """Set the currently active view for this tool.
        :param name:  The name of the view to set as active, or None is the tool has no specific view
        """

        if name != self._active_view:
            self._active_view = name
            self.activeViewChanged.emit()

    def event(self, event: Event) -> bool:
        """Handle an event.

        :param event: The event to handle.
        :return: True if this event has been handled and requires no further
            processing.
        """

        if not self._selection_pass:
            self._selection_pass = cast(SelectionPass, UM.Application.Application.getInstance().getRenderer().getRenderPass("selection"))
            if not self._selection_pass:
                return False

        if event.type == Event.ToolActivateEvent:
            if Selection.hasSelection() and self._handle:
                self._handle.setParent(self.getController().getScene().getRoot())
                self._handle.setEnabled(True)

        if event.type == Event.MouseMoveEvent and self._handle:
            event = cast(MouseEvent, event)
            if self._locked_axis != ToolHandle.NoAxis:
                return False

            tool_id = self._selection_pass.getIdAtPosition(event.x, event.y)

            if self._handle.isAxis(tool_id):
                self._handle.setActiveAxis(tool_id)
            else:
                self._handle.setActiveAxis(None)

        if event.type == Event.ToolDeactivateEvent and self._handle:
            self._handle.setParent(None)
            self._handle.setEnabled(False)
        return False

    def getController(self) -> Controller:
        """Convenience function"""
        return self._controller

    def getEnabled(self) -> bool:
        """Get the enabled state of the tool"""
        return self._enabled

    def getHandle(self) -> Optional[ToolHandle]:
        """Get the associated handle"""
        return self._handle

    def setHandle(self, handle: ToolHandle):
        """set the associated handle"""

        self._handle = handle

    def getLockedAxis(self) -> int:
        """Get which axis is locked, if any.

        :return: The ID of the axis or axes that are locked. See the `ToolHandle`
            class for the associations of IDs to each axis.
        """

        return self._locked_axis

    def setLockedAxis(self, axis: int) -> None:
        self._locked_axis = axis

        if self._handle:
            self._handle.setActiveAxis(axis)

    def getDragPlane(self) -> Optional[Plane]:
        return self._drag_plane

    def setDragPlane(self, plane: Optional[Plane]) -> None:
        self._drag_plane = plane

    def getDragStart(self) -> Optional[Vector]:
        return self._drag_start

    def setDragStart(self, x: float, y: float) -> None:
        self._drag_start = self.getDragPosition(x, y)

    def getDragPosition(self, x: float, y: float) -> Optional[Vector]:
        if not self._drag_plane:
            return None

        camera = self._controller.getScene().getActiveCamera()
        if not camera:
            return None
        ray = camera.getRay(x, y)

        target = self._drag_plane.intersectsRay(ray)
        if target:
            return ray.getPointAlongRay(target)

        return None

    def getDragVector(self, x: float, y: float) -> Optional[Vector]:
        if not self._drag_plane:
            return None

        if not self._drag_start:
            return None

        drag_end = self.getDragPosition(x, y)
        if drag_end:
            return drag_end - self._drag_start

        return None

    def setSettingToSelection(self, key: str, value: bool) -> None:
        """Set a setting on all selected objects without ancestors

        :param key: The name of the setting.
        :param value: The setting state.
        """
        sceneChanged = self._controller.getScene().sceneChanged
        for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
            selected_node.setSetting(key, value)
            sceneChanged.emit(selected_node)

    def getBoolSettingFromSelection(self, key: str, default: bool) -> Optional[bool]:
        """Get a boolean setting on selection.
        Return True or False if all the selected object agree, None otherwise.

        :param key: The name of the setting.
        :param default: The default value when the setting is not set on the object.
        """
        total_size = Selection.getCount()
        false_state_counter = 0
        true_state_counter = 0
        if not Selection.hasSelection():
            return default

        for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
            if selected_node.getSetting(key, default):
                true_state_counter += 1
            else:
                false_state_counter += 1

        if total_size == false_state_counter:  # All settings values are False
            return False
        elif total_size == true_state_counter:  # All settings values are Frue
            return True
        else:
            return None # At least one is True, but not all

    def getRequiredExtraRenderingPasses(self) -> list[str]:
        return []

    def _onToolEnabledChanged(self, tool_id: str, enabled: bool) -> None:
        if tool_id == self._plugin_id:
            self._enabled = enabled

    def _onSelectionChanged(self) -> None:
        self._selected_objects_without_selected_ancestors = None

    def _getSelectedObjectsWithoutSelectedAncestors(self) -> List[SceneNode]:
        if not isinstance(self._selected_objects_without_selected_ancestors, list):
            nodes = Selection.getAllSelectedObjects()
            self._selected_objects_without_selected_ancestors = []
            for node in nodes:
                has_selected_ancestor = False
                ancestor = node.getParent()
                while ancestor:
                    if Selection.isSelected(ancestor):
                        has_selected_ancestor = True
                        break
                    ancestor = ancestor.getParent()

                if not has_selected_ancestor:
                    self._selected_objects_without_selected_ancestors.append(node)

        return self._selected_objects_without_selected_ancestors
