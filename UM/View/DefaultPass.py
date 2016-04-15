# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.View.RenderPass import RenderPass


##  A render pass subclass that renders everything with the default parameters.
#
#   This class provides the basic rendering of the objects in the scene.
class DefaultPass(RenderPass):
    def __init__(self, width, height):
        super().__init__("default", width, height, 0)

        self._renderer = Application.getInstance().getRenderer()

    def render(self):
        self.bind()

        camera = Application.getInstance().getController().getScene().getActiveCamera()

        for batch in self._renderer.getBatches():
            batch.render(camera)

        self.release()
