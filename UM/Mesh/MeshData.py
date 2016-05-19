# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Math.Vector import Vector
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Signal import Signal, SignalEmitter
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
class MeshData(SignalEmitter):
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
        if self._vertices is None:
            return None

        return self._vertices[0 : self._vertex_count] #Only return up until point where data was filled

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
        return self._indices[0:self._face_count]

    def hasColors(self):
        return self._colors is not None

    def getColors(self):
        return self._colors[0:self._vertex_count]

    def hasUVCoordinates(self):
        return self._uvs is not None

    def getFileName(self):
        return self._file_name

    ##  Transform the meshdata by given Matrix
    #   \param transformation 4x4 homogenous transformation matrix
    def getTransformed(self, transformation):
        if self._vertices is not None:
            data = numpy.pad(self._vertices[0:self._vertex_count], ((0,0), (0,1)), "constant", constant_values=(0.0, 0.0))
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

    ## 
    # /param colors is a vertexCount by 4 numpy array with floats in range of 0 to 1.
    def setColors(self, colors):
        self._colors = colors

    ##  Get all vertices of this mesh as a bytearray
    #
    #   \return A bytearray object with 3 floats per vertex.
    def getVerticesAsByteArray(self):
        if self._vertices is not None:
            return self._vertices[0 : self._vertex_count].tostring()

    ##  Get all normals of this mesh as a bytearray
    #
    #   \return A bytearray object with 3 floats per normal.
    def getNormalsAsByteArray(self):
        if self._normals is not None:
            return self._normals[0 : self._vertex_count].tostring()

    ##  Get all indices as a bytearray
    #
    #   \return A bytearray object with 3 ints per face.
    def getIndicesAsByteArray(self):
        if self._indices is not None:
            return self._indices[0:self._face_count].tostring()

    def getColorsAsByteArray(self):
        if self._colors is not None:
            return self._colors[0 : self._vertex_count].tostring()

    def getUVCoordinatesAsByteArray(self):
        if self._uvs is not None:
            return self._uvs[0 : self._vertex_count].tostring()

    ##  Calculate the normals of this mesh, assuming it was created by using addFace (eg; the verts are connected)
    #
    #   Keyword arguments:
    #   - fast: A boolean indicating whether or not to use a fast method of normal calculation that assumes each triangle
    #           is stored as a set of three unique vertices.
    def calculateNormals(self, **kwargs):
        if self._vertices is None:
            return
        start_time = time()
        # Numpy magic!
        # First, reset the normals
        self._normals = numpy.zeros((self._vertex_count, 3), dtype=numpy.float32)

        if self.hasIndices() and not kwargs.get("fast", False):
            for face in self._indices[0:self._face_count]:
                #print(self._vertices[face[0]])
                #print(self._vertices[face[1]])
                #print(self._vertices[face[2]])
                self._normals[face[0]] = numpy.cross(self._vertices[face[0]] - self._vertices[face[1]], self._vertices[face[0]] - self._vertices[face[2]])
                length = numpy.linalg.norm(self._normals[face[0]])
                self._normals[face[0]] /= length
                self._normals[face[1]] = self._normals[face[0]]
                self._normals[face[2]] = self._normals[face[0]]
        else: #Old way of doing it, asuming that each face has 3 unique verts
            # Then, take the cross product of each pair of vectors formed from a set of three vertices.
            # The [] operator on a numpy array returns itself a numpy array. The slicing syntax is [begin:end:step],
            # so in this case we perform the cross over a two arrays. The first array is built from the difference
            # between every second item in the array starting at two and every third item in the array starting at
            # zero. The second array is built from the difference between every third item in the array starting at
            # two and every third item in the array starting at zero. The cross operation then returns an array of
            # the normals of each set of three vertices.
            n = numpy.cross(self._vertices[1:self._vertex_count:3] - self._vertices[:self._vertex_count:3], self._vertices[2:self._vertex_count:3] - self._vertices[:self._vertex_count:3])
            # We then calculate the length for each normal and perform normalization on the normals.
            l = numpy.linalg.norm(n, axis=1)
            n[:, 0] /= l
            n[:, 1] /= l
            n[:, 2] /= l
            # Finally, we store the normals per vertex, with each face normal being repeated three times, once for
            # every vertex.
            self._normals = n.repeat(3, axis=0)
        end_time = time()
        Logger.log("d", "Calculating normals took %s seconds", end_time - start_time)

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
