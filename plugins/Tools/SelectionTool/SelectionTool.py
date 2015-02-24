from UM.Event import Event
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

    def __init__(self, name):
        super().__init__(name)

        self._scene = Application.getInstance().getController().getScene()
        self._renderer = Application.getInstance().getRenderer()

        self._selection_mode = self.PixelSelectionMode

    def setSelectionMode(self, mode):
        self._selection_mode = mode


    def event(self, event):
        if event.type == Event.MouseReleaseEvent:
            Selection.clear()
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
            Selection.add(node)

    def _pixelSelection(self, event):
        selection_image = self._renderer.getSelectionImage()

        if not selection_image:
            return

        pixel = selection_image.pixel((0.5 + event.x / 2) * selection_image.width(), (0.5 + event.y / 2) * selection_image.height())
        a = (pixel & 0xff000000) >> 24
        r = (pixel & 0x00ff0000) >> 16
        g = (pixel & 0x0000ff00) >> 8
        b = (pixel & 0x000000ff) >> 0

        node = self._renderer.getSelectionMap().get((r, g, b, a), None)
        if node:
            Selection.add(node)
