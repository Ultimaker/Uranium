# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import UM.Qt.QtApplication
from UM.View.RenderPass import RenderPass


class DefaultPass(RenderPass):
    """A render pass subclass that renders everything with the default parameters.

    This class provides the basic rendering of the objects in the scene.
    """
    def __init__(self, width: int, height: int) -> None:
        super().__init__("default", width, height, 0)

        self._renderer = UM.Qt.QtApplication.QtApplication.getInstance().getRenderer()

    def render(self) -> None:
        self.bind()

        camera = UM.Qt.QtApplication.QtApplication.getInstance().getController().getScene().getActiveCamera()

        for batch in self._renderer.getBatches():
            batch.render(camera)

        self.release()


