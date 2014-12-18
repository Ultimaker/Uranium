from UM.Event import Event
from UM.Tool import Tool
from UM.Application import Application
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer

from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

class SelectionTool(Tool):
    def __init__(self, name):
        super().__init__(name)

        self._scene = Application.getInstance().getController().getScene()
        self._selection = []
        self._bboxes = {}
        self._selectionMask = 1

    def event(self, event):
        if event.type == Event.MousePressEvent:
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
                for i in self._bboxes:
                    self._bboxes[i].setParent(None)

                self._bboxes.clear()
                self._selection.clear()

                box = BoxRenderer(node.getBoundingBox(), root)
                self._bboxes[node] = box
                self._selection.append(node)
