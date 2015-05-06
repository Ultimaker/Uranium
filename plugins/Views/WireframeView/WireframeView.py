# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.View.View import View
from UM.View.Renderer import Renderer
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator


class WireframeView(View):
    def __init__(self):
        super().__init__()

    def beginRendering(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        for node in DepthFirstIterator(scene.getRoot()):
            if not node.render(renderer):
                if node.getMeshData():
                    renderer.queueNode(node, mode = Renderer.RenderWireframe)

    def endRendering(self):
        pass
