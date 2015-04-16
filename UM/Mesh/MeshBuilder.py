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

    def addLine(self, v0, v1, **kwargs):
        self._mesh_data.addVertex(v0.x, v0.y, v0.z)
        self._mesh_data.addVertex(v1.x, v1.y, v1.z)

        color = kwargs.get('color', None)
        if color:
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

    def addFace(self, v0, v1, v2, **kwargs):
        normal = kwargs.get('normal', None)
        if normal:
            self._mesh_data.addFaceWithNormals(
                                v0.x, v0.y, v0.z,
                                normal.x, normal.y, normal.z,
                                v1.x, v1.y, v1.z,
                                normal.x, normal.y, normal.z,
                                v2.x, v2.y, v2.z,
                                normal.x, normal.y, normal.z
                            )
        else:
            self._mesh_data.addFace(v0.x, v0.y, v0.z, v1.x, v1.y, v1.z, v2.x, v2.y, v2.z)

        color = kwargs.get('color', None)
        if color:
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 3, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

    def addQuad(self, v0, v1, v2, v3, **kwargs):
        self.addFace(v0, v2, v1,
            color = kwargs.get('color'),
            normal = kwargs.get('normal')
        )
        self.addFace(v0, v3, v2,
            color = kwargs.get('color'),
            normal = kwargs.get('normal')
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
            start = axis.cross(Vector.Unit_X).normalize() * radius
        else:
            start = axis.cross(Vector.Unit_Y).normalize() * radius

        angle_increment = max_angle / sections
        angle = 0

        point = start + center
        m = Matrix()
        while angle <= max_angle:
            self._mesh_data.addVertex(point.x, point.y, point.z)
            angle += angle_increment
            m.setByRotationAxis(angle, axis)
            point = start.multiply(m) + center
            self._mesh_data.addVertex(point.x, point.y, point.z)

            if color:
                self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
                self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

    def addDonut(self, **kwargs):
        inner_radius = kwargs['inner_radius']
        outer_radius = kwargs['outer_radius']
        width = kwargs['width']

        center = kwargs.get('center', Vector(0, 0, 0))
        sections = kwargs.get('sections', 32)
        color = kwargs.get('color', None)

        angle = kwargs.get('angle', 0)
        axis = kwargs.get('axis', Vector.Unit_Y)

        vertices = []
        indices = []
        colors = []

        start = self._mesh_data.getVertexCount()

        for i in range(sections):
            v1 = start + i * 3
            v2 = v1 + 1
            v3 = v1 + 2
            v4 = v1 + 3
            v5 = v1 + 4
            v6 = v1 + 5

            if i+1 >= sections: # connect the end to the start
                v4 = start
                v5 = start + 1
                v6 = start + 2

            theta = i * math.pi / (sections / 2)
            c = math.cos(theta)
            s = math.sin(theta)

            vertices.append( [inner_radius * c, inner_radius * s, 0] )
            vertices.append( [outer_radius * c, outer_radius * s, width] )
            vertices.append( [outer_radius * c, outer_radius * s, -width] )

            indices.append( [v1, v4, v5] )
            indices.append( [v2, v1, v5] )

            indices.append( [v2, v5, v6] )
            indices.append( [v3, v2, v6] )

            indices.append( [v3, v6, v4] )
            indices.append( [v1, v3, v4] )

            if color:
                colors.append( [color.r, color.g, color.b, color.a] )
                colors.append( [color.r, color.g, color.b, color.a] )
                colors.append( [color.r, color.g, color.b, color.a] )

        matrix = Matrix()
        matrix.setByRotationAxis(angle, axis)
        vertices = numpy.asarray(vertices, dtype = numpy.float32)
        vertices = vertices.dot(matrix.getData()[0:3,0:3])
        vertices[:] += center.getData()
        self._mesh_data.addVertices(vertices)

        self._mesh_data.addIndices(numpy.asarray(indices, dtype = numpy.int32))
        self._mesh_data.addColors(numpy.asarray(colors, dtype = numpy.float32))

    def addPyramid(self, **kwargs):
        width = kwargs['width']
        height = kwargs['height']
        depth = kwargs['depth']

        angle = math.radians(kwargs.get('angle', 0))
        axis = kwargs.get('axis', Vector.Unit_Y)

        center = kwargs.get('center', Vector(0, 0, 0))

        minW = -width / 2
        maxW = width / 2
        minD = -depth / 2
        maxD = depth / 2

        start = self._mesh_data.getVertexCount()

        matrix = Matrix()
        matrix.setByRotationAxis(angle, axis)
        verts = numpy.asarray([
            [minW, 0, maxD],
            [maxW, 0, maxD],
            [minW, 0, minD],
            [maxW, 0, minD],
            [0, height, 0]
        ], dtype=numpy.float32)
        verts = verts.dot(matrix.getData()[0:3,0:3])
        verts[:] += center.getData()
        self._mesh_data.addVertices(verts)

        indices = numpy.asarray([
            [start, start + 1, start + 4],
            [start + 1, start + 3, start + 4],
            [start + 3, start + 2, start + 4],
            [start + 2, start, start + 4],
            [start, start + 3, start + 1],
            [start, start + 2, start + 3]
        ], dtype=numpy.int32)
        self._mesh_data.addIndices(indices)

        color = kwargs.get('color', None)
        if color:
            vertex_count = self._mesh_data.getVertexCount()
            for i in range(1, 6):
                self._mesh_data.setVertexColor(vertex_count - i, color)
