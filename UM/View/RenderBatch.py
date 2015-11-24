# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

class RenderBatch():
    class RenderType:
        Solid = 1
        Transparent = 2
        Overlay = 3

    class RenderMode:
        Triangles = 1
        TriangleStrip = 2
        TriangleFan = 3
        Lines = 4
        LineLoop = 5
        Points = 6
        Wireframe = 7

    def __init__(self, kwargs**):
        self._render_type = kwargs.get("type", self.RenderType.Solid)
        self._render_mode = kwargs.get("mode", self.RenderMode.Triangles)
        self._material = kwargs.get("material", None)
        self._backface_cull = kwargs.get("backface_cull", True)]
        self._render_range = kwargs.get("range", None)
        self._items = kwargs.get("items", [])

    @property
    def renderType(self):
        return self._render_type

    @property
    def renderMode(self):
        return self._render_mode

    @property
    def material(self):
        return self._material

    @property
    def backfaceCull(self):
        return self._backface_cull

    @property
    def renderRange(self):
        return self._render_range

    @property
    def items(self):
        return self._items

    def addItem(self, transform, mesh):
        self._items.append((transform, mesh))
