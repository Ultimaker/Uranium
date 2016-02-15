# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.Vertex import Vertex
from UM.Math.Vector import Vector
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger

from enum import Enum

import copy
import numpy
import numpy.linalg
import hashlib
from copy import deepcopy
from time import time
numpy.seterr(all="ignore") # Ignore warnings (dev by zero)

vertexBufferProperty = "__qtgl2_vertex_buffer"
indexBufferProperty = "__qtgl2_index_buffer"


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
    def __init__(self, **kwargs):
        self._vertices = kwargs.get("vertices", None)
        self._normals = kwargs.get("normals", None)
        self._indices = kwargs.get("indices", None)
        self._colors = kwargs.get("colors", None)
        self._uvs = kwargs.get("uvs", None)
        self._vertex_count = len(self._vertices) if self._vertices is not None else 0
        self._face_count = len(self._indices) if self._indices is not None else 0
        self._type = MeshType.faces
        self._file_name = None
        # original center position
        self._center_position = None 
        self.dataChanged.connect(self._resetVertexBuffer)
        self.dataChanged.connect(self._resetIndexBuffer)
    
    dataChanged = Signal()
    
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

    def _resetIndexBuffer(self):
        try:
            delattr(self, indexBufferProperty)
        except:
            pass
    
    def setCenterPosition(self, position):
        self._center_position = position

    def getHash(self):
        m = hashlib.sha256()
        m.update(self.getVerticesAsByteArray())
        return m.hexdigest()

    def getCenterPosition(self):
        return self._center_position
    
    def _resetVertexBuffer(self):
        try:
            delattr(self, vertexBufferProperty)
        except:
            pass
    
    ##  Set the type of the mesh 
    #   \param mesh_type MeshType enum 
    def setType(self, mesh_type):
        if isinstance(mesh_type, MeshType):
            self._type = mesh_type
    
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
    
    #   Remove vertex by index or list of indices
    #   \param index Either a single index or a list of indices to be removed.
    def removeVertex(self, index):
        try: 
            #print("deleting ", index)
            #print( self._vertices) 
            self._vertices = numpy.delete(self._vertices, index,0)
            if self.hasNormals():
               self._normals = numpy.delete(self._normals,index,0)
            #print( self._vertices)    
            self._vertex_count = len(self._vertices)
        except IndexError:
            pass
        self.dataChanged.emit()
        
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

    def setFileName(self, file_name):
        self._file_name = file_name

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
            return AxisAlignedBox()

        data = numpy.pad(self._vertices[0:self._vertex_count], ((0,0), (0,1)), "constant", constant_values=(0.0, 1.0))

        if matrix is not None:
            transposed = matrix.getTransposed().getData()
            data = data.dot(transposed)
            data += transposed[:,3]
            data = data[:,0:3]

        min = data.min(axis=0)
        max = data.max(axis=0)

        return AxisAlignedBox(minimum=Vector(min[0], min[1], min[2]), maximum=Vector(max[0], max[1], max[2]))

    def clear(self):
        setattr(self, "__qtgl2_vertex_buffer", None)
        setattr(self, "__qtgl2_index_buffer", None)
        self._vertices = None
        self._normals = None
        self._indices = None
        self._colors = None
        self._uvs = None
        self._vertex_count = 0
        self._face_count = 0

    ##  Set the amount of faces before loading data to the mesh.
    #
    #   This way we can create the array before we fill it. This method will reserve
    #   `(num_faces * 3)` amount of space for vertices, `(num_faces * 3)` amount of space
    #   for normals and `num_faces` amount of space for indices.
    #
    #   \param num_faces Number of faces for which memory must be reserved.
    def reserveFaceCount(self, num_faces):
        self._vertices = numpy.zeros((num_faces * 3, 3), dtype=numpy.float32)
        self._normals = numpy.zeros((num_faces * 3, 3), dtype=numpy.float32)
        self._indices = numpy.zeros((num_faces, 3), dtype=numpy.int32)

        self._vertex_count = 0
        self._face_count = 0
    
    ##  Set the amount of verts before loading data to the mesh.
    #
    #   This way we can create the array before we fill it. This method will reserve
    #   `num_vertices` amount of space for vertices. It will not reserve space for
    #   normals or indices.
    #
    #   \param num_vertices Number of verts to be reserved.
    def reserveVertexCount(self, num_vertices):
        self._vertices = numpy.zeros((num_vertices, 3), dtype=numpy.float32)
        self._normals = None
        self._indices = None

        self._vertex_count = 0
        self._face_count = 0
    
    ##  Add a vertex to the mesh.
    #   \param x x coordinate of vertex.
    #   \param y y coordinate of vertex.
    #   \param z z coordinate of vertex.
    def addVertex(self,x,y,z):
        if self._vertices is None:
            self._vertices = numpy.zeros((10, 3), dtype=numpy.float32)

        if len(self._vertices) == self._vertex_count:
            self._vertices.resize((self._vertex_count * 2, 3))

        self._vertices[self._vertex_count, 0] = x
        self._vertices[self._vertex_count, 1] = y
        self._vertices[self._vertex_count, 2] = z
        self._vertex_count += 1
    
    ##  Add a vertex to the mesh.
    #   \param x x coordinate of vertex.
    #   \param y y coordinate of vertex.
    #   \param z z coordinate of vertex.
    #   \param nx x part of normal.
    #   \param ny y part of normal.
    #   \param nz z part of normal.
    def addVertexWithNormal(self,x,y,z,nx,ny,nz):
        if self._vertices is None:
            self._vertices = numpy.zeros((10, 3), dtype=numpy.float32)
        if self._normals is None: #Specific case, reserve vert count does not reservere size for normals
            self._normals = numpy.zeros((10, 3), dtype=numpy.float32)

        if len(self._vertices) == self._vertex_count:
            self._vertices.resize((self._vertex_count * 2, 3))

        if self._normals is None:
            self._normals = numpy.zeros((self._vertex_count, 3), dtype=numpy.float32)

        if len(self._normals) == self._vertex_count:
            self._normals.resize((self._vertex_count * 2, 3))

        self._vertices[self._vertex_count, 0] = x
        self._vertices[self._vertex_count, 1] = y
        self._vertices[self._vertex_count, 2] = z
        self._normals[self._vertex_count, 0] = nx
        self._normals[self._vertex_count, 1] = ny
        self._normals[self._vertex_count, 2] = nz
        self._vertex_count += 1
    
    ##  Add a face by providing three verts.
    #   \param x0 x coordinate of first vertex.
    #   \param y0 y coordinate of first vertex.
    #   \param z0 z coordinate of first vertex.
    #   \param x1 x coordinate of second vertex.
    #   \param y1 y coordinate of second vertex.
    #   \param z1 z coordinate of second vertex.
    #   \param x2 x coordinate of third vertex.
    #   \param y2 y coordinate of third vertex.
    #   \param z2 z coordinate of third vertex.
    def addFace(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
        if self._indices is None:
            self._indices = numpy.zeros((10, 3), dtype=numpy.int32)

        if len(self._indices) == self._face_count:
            self._indices.resize((self._face_count * 2, 3))
        
        self._indices[self._face_count, 0] = self._vertex_count
        self._indices[self._face_count, 1] = self._vertex_count + 1
        self._indices[self._face_count, 2] = self._vertex_count + 2
        self._face_count += 1

        self.addVertex(x0, y0, z0)
        self.addVertex(x1, y1, z1)
        self.addVertex(x2, y2, z2)

    ##  Add a face by providing three vertices and the normals that go with those vertices.
    #
    #   \param x0 The X coordinate of the first vertex.
    #   \param y0 The Y coordinate of the first vertex.
    #   \param z0 The Z coordinate of the first vertex.
    #   \param nx0 The X coordinate of the normal of the first vertex.
    #   \param ny0 The Y coordinate of the normal of the first vertex.
    #   \param nz0 The Z coordinate of the normal of the first vertex.
    #
    #   \param x1 The X coordinate of the second vertex.
    #   \param y1 The Y coordinate of the second vertex.
    #   \param z1 The Z coordinate of the second vertex.
    #   \param nx1 The X coordinate of the normal of the second vertex.
    #   \param ny1 The Y coordinate of the normal of the second vertex.
    #   \param nz1 The Z coordinate of the normal of the second vertex.
    #
    #   \param x2 The X coordinate of the third vertex.
    #   \param y2 The Y coordinate of the third vertex.
    #   \param z2 The Z coordinate of the third vertex.
    #   \param nx2 The X coordinate of the normal of the third vertex.
    #   \param ny2 The Y coordinate of the normal of the third vertex.
    #   \param nz2 The Z coordinate of the normal of the third vertex.
    def addFaceWithNormals(self,x0, y0, z0, nx0, ny0, nz0, x1, y1, z1, nx1, ny1, nz1, x2, y2, z2, nx2, ny2, nz2):
        if self._indices is None:
            self._indices = numpy.zeros((10, 3), dtype=numpy.int32)

        if len(self._indices) == self._face_count:
            self._indices.resize((self._face_count * 2, 3))

        self._indices[self._face_count, 0] = self._vertex_count
        self._indices[self._face_count, 1] = self._vertex_count + 1
        self._indices[self._face_count, 2] = self._vertex_count + 2
        self._face_count += 1

        self.addVertexWithNormal(x0, y0, z0, nx0, ny0, nz0)
        self.addVertexWithNormal(x1, y1, z1, nx1, ny1, nz1)
        self.addVertexWithNormal(x2, y2, z2, nx2, ny2, nz2)

    def setVertexColor(self, index, color):
        if self._colors is None:
            self._colors = numpy.zeros((10, 4), dtype=numpy.float32)

        if len(self._colors) < len(self._vertices):
            self._colors.resize((len(self._vertices), 4))

        self._colors[index, 0] = color.r
        self._colors[index, 1] = color.g
        self._colors[index, 2] = color.b
        self._colors[index, 3] = color.a

    def setVertexUVCoordinates(self, index, u, v):
        if self._uvs is None:
            self._uvs = numpy.zeros((10, 2), dtype=numpy.float32)

        if len(self._uvs) < len(self._vertices):
            self._uvs.resize((len(self._vertices), 2))

        self._uvs[index, 0] = u
        self._uvs[index, 1] = v

    def addVertices(self, vertices):
        if self._vertices is None:
            self._vertices = vertices
            self._vertex_count = len(vertices)
        else:
            self._vertices = numpy.concatenate((self._vertices[0:self._vertex_count], vertices))
            self._vertex_count  += len(vertices)

    def addIndices(self, indices):
        if self._indices is None:
            self._indices = indices
            self._face_count = len(indices)
        else:
            self._indices = numpy.concatenate((self._indices[0:self._face_count], indices))
            self._face_count += len(indices)

    def addColors(self, colors):
        if self._colors is None:
            self._colors = colors
        else:
            self._colors = numpy.concatenate((self._colors[0:self._vertex_count], colors))
    
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
