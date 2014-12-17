from UM.Event import Event

from UM.Scene.BoxRenderer import BoxRenderer
from UM.Scene.RayRenderer import RayRenderer

from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

class SelectionControls:
    def __init__(self, scene):
        self._scene = scene
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
                if node in self._selection:
                    self._bboxes[node].setParent(None)
                    del self._bboxes[node]
                    self._selection.remove(node)
                else:
                    box = BoxRenderer(node.getBoundingBox(), root)
                    self._bboxes[node] = box
                    self._selection.append(node)
