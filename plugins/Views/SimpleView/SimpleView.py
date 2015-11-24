# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Resources import Resources
from UM.Application import Application
from UM.Math.Color import Color
from UM.Preferences import Preferences

from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.View.View import View
from UM.View.GL.OpenGL import OpenGL

import math

## Standard view for mesh models.
class SimpleView(View):
    def __init__(self):
        super().__init__()

        self._material = None

    def beginRendering(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        if not self._material:
            self._material = OpenGL.getInstance().createMaterial(Resources.getPath(Resources.Shaders, "object.shader"))

        for node in DepthFirstIterator(scene.getRoot()):
            if not node.render(renderer):
                if node.getMeshData() and node.isVisible():
                    renderer.queueNode(node, material = self._material)

    def endRendering(self):
        pass
