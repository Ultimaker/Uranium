# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Event import MouseEvent, KeyEvent
from UM.Tool import Tool
from UM.Application import Application
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer
from UM.Scene.Selection import Selection
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

from PyQt5.QtGui import qAlpha, qRed, qGreen, qBlue
from PyQt5 import QtCore, QtWidgets

class SelectionTool(Tool):
    PixelSelectionMode = 1
    BoundingBoxSelectionMode = 2

    def __init__(self):
        super().__init__()

        self._scene = Application.getInstance().getController().getScene()
        self._renderer = Application.getInstance().getRenderer()

        self._selection_pass = None

        self._selection_mode = self.PixelSelectionMode
        self._ctrl_is_active = None
    
    def checkModifierKeys(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self._ctrl_is_active = modifiers == QtCore.Qt.ControlModifier

    def setSelectionMode(self, mode):
        self._selection_mode = mode

    def event(self, event):
        if self._selection_pass is None:
            self._selection_pass = self._renderer.getRenderPass("selection")

        self.checkModifierKeys(event)
        if event.type == MouseEvent.MousePressEvent and MouseEvent.LeftButton in event.buttons and self._controller.getToolsEnabled():
            if self._selection_mode == self.PixelSelectionMode:
                self._pixelSelection(event)
            else:
                self._boundingBoxSelection(event)

        return False

    def _boundingBoxSelection(self, event):
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
                if not self._ctrl_is_active:
                    Selection.clear()
                Selection.add(node)
        else:
            Selection.clear()

    def _pixelSelection(self, event):
        item_id = self._selection_pass.getIdAtPosition(event.x, event.y)

        if not item_id:
            Selection.clear()
            return

        for node in BreadthFirstIterator(self._scene.getRoot()):
            if id(node) == item_id:
                if self._ctrl_is_active:
                    if Selection.isSelected(node):
                        if node.getParent():
                            group_node = node.getParent()
                            if not group_node.callDecoration("isGroup"):
                                Selection.remove(node)
                            else:
                                while group_node.getParent().callDecoration("isGroup"):
                                    group_node = group_node.getParent()
                                Selection.remove(group_node)
                    else:
                        if node.getParent():
                            group_node = node.getParent()
                            if not group_node.callDecoration("isGroup"):
                                Selection.add(node)
                            else:
                                while group_node.getParent().callDecoration("isGroup"):
                                    group_node = group_node.getParent()
                                Selection.add(group_node)
                else:
                    if not Selection.isSelected(node) or Selection.getCount() > 1:
                        Selection.clear()
                        if node.getParent():
                            group_node = node.getParent()
                            if not group_node.callDecoration("isGroup"):
                                Selection.add(node)
                            else:
                                while group_node.getParent().callDecoration("isGroup"):
                                    group_node = group_node.getParent()
                                Selection.add(group_node)
