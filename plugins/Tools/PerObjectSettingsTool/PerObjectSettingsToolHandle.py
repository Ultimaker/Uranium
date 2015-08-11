# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Math.Color import Color

from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection

from UM.Mesh.MeshBuilder import MeshBuilder

class PerObjectSettingsToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._scene.sceneChanged.connect(self._update)
        self._update(None)

        self._auto_scale = False

        Selection.selectionCenterChanged.disconnect(self._onSelectionCenterChanged)

    def _update(self, source):
        if source == self:
            return

        mb = MeshBuilder()

        for node in BreadthFirstIterator(self._scene.getRoot()):
            if type(node) is not SceneNode or not node.getMeshData():
                continue

            mb.addCube(
                width = 4,
                height = 4,
                depth = 4,
                center = node.getWorldPosition(),
                color = Color(1.0, 1.0, 1.0, 1.0)
            )

        self.setSolidMesh(mb.getData())
        #self.setSelectionMesh(mb.getData())
