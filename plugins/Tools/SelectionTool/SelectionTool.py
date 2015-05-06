# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Event import MouseEvent
from UM.Tool import Tool
from UM.Application import Application
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer
from UM.Scene.Selection import Selection
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

from PyQt5.QtGui import qAlpha, qRed, qGreen, qBlue

class SelectionTool(Tool):
    PixelSelectionMode = 1
    BoundingBoxSelectionMode = 2

    def __init__(self):
        super().__init__()

        self._scene = Application.getInstance().getController().getScene()
        self._renderer = Application.getInstance().getRenderer()

        self._selection_mode = self.PixelSelectionMode

    def setSelectionMode(self, mode):
        self._selection_mode = mode

    def event(self, event):
        if event.type == MouseEvent.MouseReleaseEvent and MouseEvent.LeftButton in event.buttons:
            if self._selection_mode == self.PixelSelectionMode:
                self._pixelSelection(event)
            else:
                self._boundingBoxSelection(event)

    def _boundingBoxSelection(self, event):
        root = self._scene.getRoot()

        ray = self._scene.getActiveCamera().getRay(event.x, event.y)

        intersections = []
        for node in BreadthFirstIterator(root):
            if node.getSelectionMask() == self._selectionMask and not node.isLocked():
                intersection = node.getBoundingBox().intersectsRay(ray)
                if intersection:
                    intersections.append((node, intersection[0], intersection[1]))

        if intersections:
            intersections.sort(key=lambda k: k[1])

            node = intersections[0][0]
            if not Selection.isSelected(node):
                Selection.clear()
                Selection.add(node)
        else:
            Selection.clear()

    def _pixelSelection(self, event):
        pixel_id = self._renderer.getIdAtCoordinate(event.x, event.y)

        if not pixel_id:
            Selection.clear()
            return

        for node in BreadthFirstIterator(self._scene.getRoot()):
            if id(node) == pixel_id:
                if not Selection.isSelected(node):
                    Selection.clear()
                    Selection.add(node)
