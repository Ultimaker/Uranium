from UM.Mesh.MeshData import MeshData
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix

import numpy
import math

class MeshBuilder:
    def __init__(self):
        self._mesh_data = MeshData()

    def getData(self):
        return self._mesh_data

    def addFace(self, v0, v1, v2, **kwargs):
        self._mesh_data.addFace(v0.x, v0.y, v0.z, v1.x, v1.y, v1.z, v2.x, v2.y, v2.z)

        color = kwargs.get('color', None)
        if color:
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 3, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

    def addQuad(self, v0, v1, v2, v3, **kwargs):
        self._mesh_data.addFace(
            v0.x, v0.y, v0.z,
            v2.x, v2.y, v2.z,
            v1.x, v1.y, v1.z,
            color = kwargs.get('color')
        )
        self._mesh_data.addFace(
            v0.x, v0.y, v0.z,
            v3.x, v3.y, v3.z,
            v2.x, v2.y, v2.z,
            color = kwargs.get('color')
        )

    def addCube(self, **kwargs):
        width = kwargs['width']
        height = kwargs['height']
        depth = kwargs['depth']

        center = kwargs.get('center', Vector(0, 0, 0))

        minW = -width / 2 + center.x
        maxW = width / 2 + center.x
        minH = -height / 2 + center.y
        maxH = height / 2 + center.y
        minD = -depth / 2 + center.z
        maxD = depth / 2 + center.z

        start = self._mesh_data.getVertexCount()

        verts = numpy.asarray([
            [minW, minH, maxD],
            [minW, maxH, maxD],
            [maxW, maxH, maxD],
            [maxW, minH, maxD],
            [minW, minH, minD],
            [minW, maxH, minD],
            [maxW, maxH, minD],
            [maxW, minH, minD],
        ], dtype=numpy.float32)
        self._mesh_data.addVertices(verts)

        indices = numpy.asarray([
            [start, start + 2, start + 1],
            [start, start + 3, start + 2],

            [start + 3, start + 7, start + 6],
            [start + 3, start + 6, start + 2],

            [start + 7, start + 5, start + 6],
            [start + 7, start + 4, start + 5],

            [start + 4, start + 1, start + 5],
            [start + 4, start + 0, start + 1],

            [start + 1, start + 6, start + 5],
            [start + 1, start + 2, start + 6],

            [start + 0, start + 7, start + 3],
            [start + 0, start + 4, start + 7]
        ], dtype=numpy.int32)
        self._mesh_data.addIndices(indices)

        color = kwargs.get('color', None)
        if color:
            vertex_count = self._mesh_data.getVertexCount()
            for i in range(1, 9):
                self._mesh_data.setVertexColor(vertex_count - i, color)

    def addArc(self, **kwargs):
        radius = kwargs['radius']
        axis = kwargs['axis']

        max_angle = kwargs.get('angle', math.pi * 2)
        center = kwargs.get('center', Vector(0, 0, 0))
        sections = kwargs.get('sections', 32)
        color = kwargs.get('color', None)

        if axis == Vector.Unit_Y:
            start = axis.cross(Vector.Unit_X) * radius
        else:
            start = axis.cross(Vector.Unit_Y) * radius

        angle_increment = max_angle / sections
        angle = 0

        point = start
        m = Matrix()
        while angle <= max_angle:
            self._mesh_data.addVertex(point.x, point.y, point.z)
            angle += angle_increment
            m.setByRotationAxis(angle, axis)
            point = start.multiply(m)
            self._mesh_data.addVertex(point.x, point.y, point.z)

            if color:
                self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
                self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

