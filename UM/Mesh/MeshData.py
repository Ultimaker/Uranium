# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Math.Vector import Vector
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Logger import Logger

from enum import Enum

from UM.View.GL.OpenGL import OpenGL

import numpy
import numpy.linalg
import scipy.spatial
import hashlib
from copy import deepcopy
from time import time
numpy.seterr(all="ignore") # Ignore warnings (dev by zero)


class MeshType(Enum):
    faces = 1 # Start at one, as 0 is false (so if this is used in a if statement, it's always true)
    pointcloud = 2


##  Class to hold a list of verts and possibly how (and if) they are connected.
#
#   This class stores three numpy arrays that contain the data for a mesh. Vertices
#   are stored as a two-dimensional array of floats with the rows being individual
#   vertices and the three columns being the X, Y and Z components of the vertices.
#   Normals are stored in the same manner and kept in sync with the vertices. Indices
#   are stored as a two-dimensional array of integers with the rows being the individual
#   faces and the three columns being the indices that refer to the individual vertices.
class MeshData:
    def __init__(self, vertices=None, normals=None, indices=None, colors=None, uvs=None, file_name=None,
                 center_position=None):
        self._vertices = immutableNDArray(vertices)
        self._normals = immutableNDArray(normals)
        self._indices = immutableNDArray(indices)
        self._colors = immutableNDArray(colors)
        self._uvs = immutableNDArray(uvs)
        self._vertex_count = len(self._vertices) if self._vertices is not None else 0
        self._face_count = len(self._indices) if self._indices is not None else 0
        self._type = MeshType.faces
        self._file_name = None
        # original center position
        self._center_position = center_position
        self._convex_hull = None    # type: scipy.spatial.qhull.ConvexHull
        self._convex_hull_vertices = None

    def __deepcopy__(self, memo):
        copy = MeshData()
        copy._vertices = deepcopy(self._vertices, memo)
        copy._normals = deepcopy(self._normals, memo)
        copy._indices = deepcopy(self._indices, memo)
        copy._colors = deepcopy(self._colors, memo)
        copy._uvs = deepcopy(self._uvs, memo)
        copy._vertex_count = deepcopy(self._vertex_count, memo)
        copy._face_count = deepcopy(self._face_count, memo)
        copy._type = deepcopy(self._type, memo)
        copy._file_name = deepcopy(self._file_name, memo)
        self._center_position = deepcopy (self._center_position, memo)
        return copy

    def set(self, vertices=None, normals=None, indices=None, colors=None, uvs=None, file_name=None,
            center_position=None):
        vertices = vertices if vertices is not None else self._vertices
        normals = normals if normals is not None else self._normals
        indices = indices if indices is not None else self._indices
        colors = colors if colors is not None else self._colors
        uvs = uvs if uvs is not None else self._uvs
        file_name = file_name if file_name is not None else self._file_name
        center_position = center_position if center_position is not None else self._center_position

        return MeshData(vertices=vertices, normals=normals, indices=indices, colors=colors, uvs=uvs,
                        file_name=file_name, center_position=center_position)

    def setCenterPosition(self, position):
        self._center_position = position

    def getHash(self):
        m = hashlib.sha256()
        m.update(self.getVerticesAsByteArray())
        return m.hexdigest()

    def getCenterPosition(self):
        return self._center_position

    def getType(self):
        return self._type

    def getFaceCount(self):
        return self._face_count

    ##  Get the array of vertices
    def getVertices(self):
        return self._vertices

    ##  Get the number of vertices
    def getVertexCount(self):
        return self._vertex_count

    ##  Get a vertex by index
    def getVertex(self, index):
        try:
            return self._vertices[index]
        except IndexError:
            return None

    ##  Return whether this mesh has vertex normals.
    def hasNormals(self):
        return self._normals is not None

    ##  Return the list of vertex normals.
    def getNormals(self):
        return self._normals

    ##  Return whether this mesh has indices.
    def hasIndices(self):
        return self._indices is not None

    ##  Get the array of indices
    #   \return \type{numpy.ndarray}
    def getIndices(self):
        return self._indices

    def hasColors(self):
        return self._colors is not None

    def getColors(self):
        return self._colors

    def hasUVCoordinates(self):
        return self._uvs is not None

    def getFileName(self):
        return self._file_name

    ##  Transform the meshdata by given Matrix
    #   \param transformation 4x4 homogenous transformation matrix
    def getTransformed(self, transformation):
        if self._vertices is not None:
            data = numpy.pad(self._vertices, ((0,0), (0,1)), "constant", constant_values=(0.0, 0.0))
            data = data.dot(transformation.getTransposed().getData())
            data += transformation.getData()[:,3]
            data = data[:,0:3]

            mesh = deepcopy(self)
            mesh._vertices = data
            return mesh
        else:
            return MeshData(vertices = self._vertices)

    ##  Get the extents of this mesh.
    #
    #   \param matrix The transformation matrix from model to world coordinates.
    def getExtents(self, matrix = None):
        if self._vertices is None:
            return None

        data = numpy.pad(self.getConvexHullVertices(), ((0, 0), (0, 1)), "constant", constant_values=(0.0, 1.0))

        if matrix is not None:
            transposed = matrix.getTransposed().getData()
            data = data.dot(transposed)
            data += transposed[:, 3]
            data = data[:, 0:3]

        min = data.min(axis=0)
        max = data.max(axis=0)

        return AxisAlignedBox(minimum=Vector(min[0], min[1], min[2]), maximum=Vector(max[0], max[1], max[2]))

    def setVertexUVCoordinates(self, index, u, v):
        if self._uvs is None:
            self._uvs = numpy.zeros((10, 2), dtype=numpy.float32)

        if len(self._uvs) < len(self._vertices):
            self._uvs.resize((len(self._vertices), 2))

        self._uvs[index, 0] = u
        self._uvs[index, 1] = v

    ##  Get all vertices of this mesh as a bytearray
    #
    #   \return A bytearray object with 3 floats per vertex.
    def getVerticesAsByteArray(self):
        if self._vertices is None:
            return None
        # FIXME cache result
        return self._vertices.tostring()

    ##  Get all normals of this mesh as a bytearray
    #
    #   \return A bytearray object with 3 floats per normal.
    def getNormalsAsByteArray(self):
        if self._normals is None:
            return None
        # FIXME cache result
        return self._normals.tostring()

    ##  Get all indices as a bytearray
    #
    #   \return A bytearray object with 3 ints per face.
    def getIndicesAsByteArray(self):
        if self._indices is None:
            return None
        # FIXME cache result
        return self._indices.tostring()

    def getColorsAsByteArray(self):
        if self._colors is None:
            return None
        # FIXME cache result
        return self._colors.tostring()

    def getUVCoordinatesAsByteArray(self):
        if self._uvs is not None:
            return self._uvs[0 : self._vertex_count].tostring()

    #######################################################################
    # Convex hull handling
    #######################################################################

    def _computeConvexHull(self):
        points = self.getVertices()
        if points is None:
            return

        start_time = time()
        self._convex_hull = scipy.spatial.ConvexHull(points)
        end_time = time()
        Logger.log("d", "Calculating 3D convex hull took %s seconds. %s input vertices. %s output vertices.",
                   end_time - start_time, len(points), len(self._convex_hull.vertices))

    ##  Gets the Convex Hull points
    #
    def getConvexHull(self):
        # Returns type: scipy.spatial.qhull.ConvexHull
        if self._convex_hull is None:
            self._computeConvexHull()
        return self._convex_hull

    def getConvexHullVertices(self):
        if self._convex_hull_vertices is None:
            convex_hull = self.getConvexHull()
            self._convex_hull_vertices = numpy.take(convex_hull.points, convex_hull.vertices, axis=0)
        return self._convex_hull_vertices

    def toString(self):
        return "MeshData(_vertices=" + str(self._vertices) + ", _normals=" + str(self._normals) + ", _indices=" + \
               str(self._indices) + ", _colors=" + str(self._colors) + ", _uvs=" + str(self._uvs) + ") "
##
#
def immutableNDArray(nda):
    if nda is None:
        return None
    if not nda.flags.writeable:
        return nda
    copy = deepcopy(nda)
    copy.flags.writeable = False
    return copy
