# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.MeshData import MeshData
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix

import numpy
import math

##  Builds new meshes by adding primitives.
#
#   This class functions in much the same way as a normal StringBuilder would.
#   Each instance of MeshBuilder creates one mesh. This mesh starts empty, but
#   you can add primitives to it via the various methods of this class. The
#   result can then be converted to a normal mesh.
class MeshBuilder:
    ##  Creates a new MeshBuilder with an empty mesh.
    def __init__(self):
        self._mesh_data = MeshData()

    ##  Gets the mesh that was built by this MeshBuilder.
    #
    #   Note that this gets a reference to the mesh. Adding more primitives to
    #   the MeshBuilder will cause the mesh returned by this function to change
    #   as well.
    #
    #   \return A mesh with all the primitives added to this MeshBuilder.
    def getData(self):
        return self._mesh_data

    ##  Adds a 3-dimensional line to the mesh of this mesh builder.
    #
    #   \param v0 One endpoint of the line to add.
    #   \param v1 The other endpoint of the line to add.
    #   \param color (Optional) The colour of the line, if any. If no colour is
    #   provided, the colour is determined by the shader.
    def addLine(self, v0, v1, color = None):
        self._mesh_data.addVertex(v0.x, v0.y, v0.z)
        self._mesh_data.addVertex(v1.x, v1.y, v1.z)

        if color: #Add colours to the vertices, if we have them.
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

    ##  Adds a triangle to the mesh of this mesh builder.
    #
    #   \param v0 The first corner of the triangle.
    #   \param v1 The second corner of the triangle.
    #   \param v2 The third corner of the triangle.
    #   \param normal (Optional) The normal vector for the triangle. If no
    #   normal vector is provided, it will be calculated automatically.
    #   \param color (Optional) The colour for the triangle. If no colour is
    #   provided, the colour is determined by the shader.
    def addFace(self, v0, v1, v2, normal = None, color = None):
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
            self._mesh_data.addFace(v0.x, v0.y, v0.z, v1.x, v1.y, v1.z, v2.x, v2.y, v2.z) #Computes the normal by itself.

        if color: #Add colours to the vertices if we have them.
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 3, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
            self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

    ##  Add a quadrilateral to the mesh of this mesh builder.
    #
    #   The quadrilateral will be constructed as two triangles. v0 and v2 are
    #   the two vertices across the diagonal of the quadrilateral.
    #
    #   \param v0 The first corner of the quadrilateral.
    #   \param v1 The second corner of the quadrilateral.
    #   \param v2 The third corner of the quadrilateral.
    #   \param v3 The fourth corner of the quadrilateral.
    #   \param normal (Optional) The normal vector for the quadrilateral. Both
    #   triangles will get the same normal vector, if provided. If no normal
    #   vector is provided, the normal vectors for both triangles are computed
    #   automatically.
    #   \param color (Optional) The colour for the quadrilateral. If no colour
    #   is provided, the colour is determined by the shader.
    def addQuad(self, v0, v1, v2, v3, normal = None, color = None):
        self.addFace(v0, v2, v1,
            color = color,
            normal = normal
        )
        self.addFace(v0, v3, v2, #v0 and v2 are shared with the other triangle!
            color = color,
            normal = normal
        )

    ##  Add a rectangular cuboid to the mesh of this mesh builder.
    #
    #   A rectangular cuboid is a square block with arbitrary width, height and
    #   depth.
    #
    #   \param width The size of the rectangular cuboid in the X dimension.
    #   \param height The size of the rectangular cuboid in the Y dimension.
    #   \param depth The size of the rectangular cuboid in the Z dimension.
    #   \param center (Optional) The position of the centre of the rectangular
    #   cuboid in space. If not provided, the cuboid is placed at the coordinate
    #   origin.
    #   \param color (Optional) The colour for the rectangular cuboid. If no
    #   colour is provided, the colour is determined by the shader.
    def addCube(self, width, height, depth, center = Vector(0, 0, 0), color = None):
        #Compute the actual positions of the planes.
        minW = -width / 2 + center.x
        maxW = width / 2 + center.x
        minH = -height / 2 + center.y
        maxH = height / 2 + center.y
        minD = -depth / 2 + center.z
        maxD = depth / 2 + center.z

        start = self._mesh_data.getVertexCount()

        verts = numpy.asarray([ #All 8 corners.
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

        indices = numpy.asarray([ #All 6 quads (12 triangles).
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

        if color: #If we have a colour, add a colour to all of the vertices.
            vertex_count = self._mesh_data.getVertexCount()
            for i in range(1, 9):
                self._mesh_data.setVertexColor(vertex_count - i, color)

    ##  Add an arc to the mesh of this mesh builder.
    #
    #   An arc is a curve that is also a segment of a circle.
    #
    #   \param radius The radius of the circle this arc is a segment of.
    #   \param axis The axis perpendicular to the plane on which the arc lies.
    #   \param angle (Optional) The length of the arc, in radians. If not
    #   provided, the entire circle is used (2 pi).
    #   \param center (Optional) The position of the centre of the arc in space.
    #   If no position is provided, the arc is centred around the coordinate
    #   origin.
    #   \param sections (Optional) The resolution of the arc. The arc is
    #   approximated by this number of line segments.
    #   \param color (Optional) The colour for the arc. If no colour is
    #   provided, the colour is determined by the shader.
    def addArc(self, radius, axis, angle = math.pi * 2, center = Vector(0, 0, 0), sections = 32, color = None):
        #We'll compute the vertices of the arc by computing an initial point and
        #rotating the initial point with a rotation matrix.
        if axis == Vector.Unit_Y:
            start = axis.cross(Vector.Unit_X).normalize() * radius
        else:
            start = axis.cross(Vector.Unit_Y).normalize() * radius

        angle_increment = angle / sections
        current_angle = 0

        point = start + center
        m = Matrix()
        while current_angle <= angle: #Add each of the vertices.
            self._mesh_data.addVertex(point.x, point.y, point.z)
            current_angle += angle_increment
            m.setByRotationAxis(current_angle, axis)
            point = start.multiply(m) + center #Get the next vertex by rotating the start position with a matrix.
            self._mesh_data.addVertex(point.x, point.y, point.z)

            if color: #If we have a colour, add that colour to the new vertex.
                self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 2, color)
                self._mesh_data.setVertexColor(self._mesh_data.getVertexCount() - 1, color)

    ##  Adds a torus to the mesh of this mesh builder.
    #
    #   The torus is the shape of a doughnut. This doughnut is delicious and
    #   moist, but not very healthy.
    #
    #   \param inner_radius The radius of the hole inside the torus. Must be
    #   smaller than outer_radius.
    #   \param outer_radius The radius of the outside of the torus. Must be
    #   larger than inner_radius.
    #   \param width The radius of the torus in perpendicular direction to its
    #   perimeter. This is the "thickness".
    #   \param center (Optional) The position of the centre of the torus. If no
    #   position is provided, the torus will be centred around the coordinate
    #   origin.
    #   \param sections (Optional) The resolution of the torus in the
    #   circumference. The resolution of the intersection of the torus cannot be
    #   changed.
    #   \param color (Optional) The colour of the torus. If no colour is
    #   provided, a colour will be determined by the shader.
    #   \param angle (Optional) An angle of rotation to rotate the torus by, in
    #   radians.
    #   \param axis (Optional) An axis of rotation to rotate the torus around.
    #   If no axis is provided and the angle of rotation is nonzero, the torus
    #   will be rotated around the Y-axis.
    def addDonut(self, inner_radius, outer_radius, width, center = Vector(0, 0, 0), sections = 32, color = None, angle = 0, axis = Vector.Unit_Y):
        vertices = []
        indices = []
        colors = []

        start = self._mesh_data.getVertexCount() #Starting index.

        for i in range(sections):
            v1 = start + i * 3 #Indices for each of the vertices we'll add for this section.
            v2 = v1 + 1
            v3 = v1 + 2
            v4 = v1 + 3
            v5 = v1 + 4
            v6 = v1 + 5

            if i+1 >= sections: # connect the end to the start
                v4 = start
                v5 = start + 1
                v6 = start + 2

            theta = i * math.pi / (sections / 2) #Angle of this piece around torus perimeter.
            c = math.cos(theta) #X-coordinate around torus perimeter.
            s = math.sin(theta) #Y-coordinate around torus perimeter.

            #One vertex on the inside perimeter, two on the outside perimiter (up and down).
            vertices.append( [inner_radius * c, inner_radius * s, 0] )
            vertices.append( [outer_radius * c, outer_radius * s, width] )
            vertices.append( [outer_radius * c, outer_radius * s, -width] )

            #Connect the vertices to the next segment.
            indices.append( [v1, v4, v5] )
            indices.append( [v2, v1, v5] )

            indices.append( [v2, v5, v6] )
            indices.append( [v3, v2, v6] )

            indices.append( [v3, v6, v4] )
            indices.append( [v1, v3, v4] )

            if color: #If we have a colour, add it to the vertices.
                colors.append( [color.r, color.g, color.b, color.a] )
                colors.append( [color.r, color.g, color.b, color.a] )
                colors.append( [color.r, color.g, color.b, color.a] )

        #Rotate the resulting torus around the specified axis.
        matrix = Matrix()
        matrix.setByRotationAxis(angle, axis)
        vertices = numpy.asarray(vertices, dtype = numpy.float32)
        vertices = vertices.dot(matrix.getData()[0:3, 0:3])
        vertices[:] += center.getData() #And translate to the desired position.

        self._mesh_data.addVertices(vertices)
        self._mesh_data.addIndices(numpy.asarray(indices, dtype = numpy.int32))
        self._mesh_data.addColors(numpy.asarray(colors, dtype = numpy.float32))

    ##  Adds a pyramid to the mesh of this mesh builder.
    #
    #   \param width The width of the base of the pyramid.
    #   \param height The height of the pyramid (from base to notch).
    #   \param depth The depth of the base of the pyramid.
    #   \param angle (Optional) An angle of rotation to rotate the pyramid by,
    #   in degrees.
    #   \param axis (Optional) An axis of rotation to rotate the pyramid around.
    #   If no axis is provided and the angle of rotation is nonzero, the pyramid
    #   will be rotated around the Y-axis.
    #   \param center (Optional) The position of the centre of the base of the
    #   pyramid. If not provided, the pyramid will be placed on the coordinate
    #   origin.
    #   \param color (Optional) The colour of the pyramid. If no colour is
    #   provided, a colour will be determined by the shader.
    def addPyramid(self, width, height, depth, angle = 0, axis = Vector.Unit_Y, center = Vector(0, 0, 0), color = None):
        angle = math.radians(angle)

        minW = -width / 2
        maxW = width / 2
        minD = -depth / 2
        maxD = depth / 2

        start = self._mesh_data.getVertexCount() #Starting index.

        matrix = Matrix()
        matrix.setByRotationAxis(angle, axis)
        verts = numpy.asarray([ #All 5 vertices of the pyramid.
            [minW, 0, maxD],
            [maxW, 0, maxD],
            [minW, 0, minD],
            [maxW, 0, minD],
            [0, height, 0]
        ], dtype=numpy.float32)
        verts = verts.dot(matrix.getData()[0:3,0:3]) #Rotate the pyramid around the axis.
        verts[:] += center.getData()
        self._mesh_data.addVertices(verts)

        indices = numpy.asarray([ #Connect the vertices to each other (6 triangles).
            [start, start + 1, start + 4], #The four sides of the pyramid.
            [start + 1, start + 3, start + 4],
            [start + 3, start + 2, start + 4],
            [start + 2, start, start + 4],
            [start, start + 3, start + 1], #The base of the pyramid.
            [start, start + 2, start + 3]
        ], dtype=numpy.int32)
        self._mesh_data.addIndices(indices)

        if color: #If we have a colour, add the colour to each of the vertices.
            vertex_count = self._mesh_data.getVertexCount()
            for i in range(1, 6):
                self._mesh_data.setVertexColor(vertex_count - i, color)
