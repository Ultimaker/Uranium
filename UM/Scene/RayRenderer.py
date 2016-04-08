# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.ToolHandle import ToolHandle


class RayRenderer(ToolHandle):
    def __init__(self, ray, parent = None):
        super().__init__(parent)

        md = self.getMeshData()

        md.addVertex(0, 0, 0)
        md.addVertex(ray.direction.x * 500, ray.direction.y * 500, ray.direction.z * 500)

        self.setPosition(ray.origin)
