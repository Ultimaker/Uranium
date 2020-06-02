# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5 import QtCore, QtWidgets

from UM.Application import Application
from UM.Event import MouseEvent
from UM.Logger import Logger
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.Selection import Selection
from UM.Tool import Tool


class SelectionTool(Tool):
    """Provides the tool to select meshes and groups

    Note that the tool has two implementations for different modes of selection:
    Pixel Selection Mode and BoundingBox Selection Mode. Of these two, only Pixel Selection Mode
    is in active use. BoundingBox Selection Mode may not be functional.
    """

    PixelSelectionMode = 1
    BoundingBoxSelectionMode = 2

    def __init__(self):
        super().__init__()

        self._scene = Application.getInstance().getController().getScene()
        self._renderer = Application.getInstance().getRenderer()

        self._selection_pass = None

        self._selection_mode = self.PixelSelectionMode
        self._ctrl_is_active = None  # Ctrl modifier key is used for sub-selection
        self._alt_is_active = None
        self._shift_is_active = None  # Shift modifier key is used for multi-selection

    def checkModifierKeys(self, event):
        """Prepare modifier-key variables on each event

        :param event: type(Event) event passed from event handler
        """

        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self._shift_is_active = modifiers & QtCore.Qt.ShiftModifier
        self._ctrl_is_active = modifiers & QtCore.Qt.ControlModifier
        self._alt_is_active = modifiers & QtCore.Qt.AltModifier

    def setSelectionMode(self, mode):
        """Set the selection mode

        The tool has two implementations for different modes of selection: PixelSelectionMode and BoundingboxSelectionMode.
        Of these two, only Pixel Selection Mode is in active use. BoundingBox Selection Mode may not be functional.
        :param mode: type(SelectionTool enum)
        """

        self._selection_mode = mode

    def event(self, event):
        """Handle mouse and keyboard events

        :param event: type(Event)
        """

        # The selection renderpass is used to identify objects in the current view
        if self._selection_pass is None:
            self._selection_pass = self._renderer.getRenderPass("selection")

        self.checkModifierKeys(event)
        #if event.type == MouseEvent.MouseMoveEvent and Selection.getFaceSelectMode():
        #    return self._pixelHover(event)
        if event.type == MouseEvent.MousePressEvent and MouseEvent.LeftButton in event.buttons and self._controller.getToolsEnabled():
            # Perform a selection operation
            if self._selection_mode == self.PixelSelectionMode:
                return self._pixelSelection(event)
            else:
                self._boundingBoxSelection(event)
        elif event.type == MouseEvent.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            Application.getInstance().getController().toolOperationStopped.emit(self)
        return False

    def _boundingBoxSelection(self, event):
        """Handle mouse and keyboard events for bounding box selection

        :param event: type(Event) passed from self.event()
        """

        root = self._scene.getRoot()

        ray = self._scene.getActiveCamera().getRay(event.x, event.y)

        intersections = []
        for node in BreadthFirstIterator(root):
            if node.isEnabled() and not node.isLocked():
                intersection = node.getBoundingBox().intersectsRay(ray)
                if intersection:
                    intersections.append((node, intersection[0], intersection[1]))

        if intersections:
            intersections.sort(key=lambda k: k[1])

            node = intersections[0][0]
            if not Selection.isSelected(node):
                if not self._shift_is_active:
                    Selection.clear()
                Selection.add(node)
        else:
            Selection.clear()

    def _pixelSelection(self, event):
        """Handle mouse and keyboard events for pixel selection

        :param event: type(Event) passed from self.event()
        """

        # Find a node id by looking at a pixel value at the requested location
        if self._selection_pass:
            if Selection.getFaceSelectMode():
                item_id = id(Selection.getSelectedObject(0))
            else:
                item_id = self._selection_pass.getIdAtPosition(event.x, event.y)
        else:
            Logger.log("w", "Selection pass is None. getRenderPass('selection') returned None")
            return False

        if not item_id and not self._shift_is_active:
            if Selection.hasSelection():
                Selection.clearFace()
                Selection.clear()
                return True
            return False  # Nothing was selected before and the user didn't click on an object.

        # Find the scene-node which matches the node-id
        for node in BreadthFirstIterator(self._scene.getRoot()):
            if id(node) != item_id:
                continue

            if self._isNodeInGroup(node):
                is_selected = Selection.isSelected(self._findTopGroupNode(node))
            else:
                is_selected = Selection.isSelected(node)

            if self._shift_is_active:
                if is_selected:
                    # Deselect the SceneNode and its siblings in a group
                    if node.getParent():
                        if self._ctrl_is_active or not self._isNodeInGroup(node):
                            Selection.remove(node)
                        else:
                            Selection.remove(self._findTopGroupNode(node))
                        return True
                else:
                    # Select the SceneNode and its siblings in a group
                    if node.getParent():
                        if self._ctrl_is_active or not self._isNodeInGroup(node):
                            Selection.add(node)
                        else:
                            Selection.add(self._findTopGroupNode(node))
                        return True
            else:
                if Selection.getFaceSelectMode():
                    face_id = self._selection_pass.getFaceIdAtPosition(event.x, event.y)
                    if face_id >= 0:
                        Selection.toggleFace(node, face_id)
                    else:
                        Selection.clear()
                        Selection.clearFace()
                if not is_selected or Selection.getCount() > 1:
                    # Select only the SceneNode and its siblings in a group
                    Selection.clear()
                    if node.getParent():
                        if self._ctrl_is_active or not self._isNodeInGroup(node):
                            Selection.add(node)
                        else:
                            Selection.add(self._findTopGroupNode(node))
                        return True
                elif self._isNodeInGroup(node) and self._ctrl_is_active:
                    Selection.clear()
                    Selection.add(node)
                    return True

        return False

    def _pixelHover(self, event):
        if Selection.getFaceSelectMode():
            face_id = self._selection_pass.getFaceIdAtPosition(event.x, event.y)
            if face_id >= 0:
                Selection.hoverFace(Selection.getSelectedObject(0), face_id)
            else:
                Selection.clearFace()
            return True
        return False

    def _isNodeInGroup(self, node):
        """Check whether a node is in a group

        :param node: type(SceneNode)
        :return: in_group type(boolean)
        """

        parent_node = node.getParent()
        if not parent_node:
            return False
        return parent_node.callDecoration("isGroup")

    def _findTopGroupNode(self, node):
        """Get the top root group for a node

        :param node: type(SceneNode)
        :return: group type(SceneNode)
        """

        group_node = node
        while group_node.getParent().callDecoration("isGroup"):
            group_node = group_node.getParent()
        return group_node
