from UM.MeshHandling.Vertex import Vertex
from UM.Math.Vector import Vector
from UM.Math.AxisAlignedBox import AxisAlignedBox

import numpy
import numpy.linalg

##  Class to hold a list of verts and possibly how (and if) they are connected.
#
#   This class stores three numpy arrays that contain the data for a mesh. Vertices
#   are stored as a two-dimensional array of floats with the rows being individual
#   vertices and the three columns being the X, Y and Z components of the vertices.
#   Normals are stored in the same manner and kept in sync with the vertices. Indices
#   are stored as a two-dimensional array of integers with the rows being the individual
#   faces and the three columns being the indices that refer to the individual vertices.
class MeshData(object):
    def __init__(self):
        self._vertices = None
        self._normals = None
        self._indices = None
        self._vertex_count = 0
        self._face_count = 0
        
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
        return self._face_indices
    
    ##  Transform the meshdata by given Matrix
    #   \param transformation 4x4 homogenous transformation matrix
    def transform(self, transformation):
        #TODO: Implement
        pass

    ##  Get the extents of this mesh.
    #
    #
    def getExtents(self, matrix = None):
        if self._vertices is None:
            return AxisAlignedBox()

        data = numpy.pad(self._vertices.copy(), (0,1), 'constant', constant_values=(0.0, 1.0))

        if matrix is not None:
            data = data.dot(matrix.getData())

        data += matrix.getData()[:,3]

        min = data.min(axis=0)
        max = data.max(axis=0)

        return AxisAlignedBox(rightTopFront=Vector(max[0], max[1], max[2]), leftBottomBack=Vector(min[0], min[1], min[2]))
    
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
            self.reserveVertexCount(10)

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
            self.reserveVertexCount(10)

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
            return self._indices[0 : self._face_count].tostring()

    ##  Calculate the normals of this mesh, assuming it was created by using addFace (eg; the verts are connected)    
    def calculateNormals(self):
        # Numpy magic!
        # First, reset the normals
        self._normals = numpy.zeros((self._vertex_count, 3), dtype=numpy.float32)

        # Then, take the cross product of each pair of vectors formed from a set of three vertices.
        # The [] operator on a numpy array returns itself a numpy array. The slicing syntax is [begin:end:step],
        # so in this case we perform the cross over a two arrays. The first array is built from  the difference
        # between every second item in the array starting at two and every third item in the array starting at
        # zero. The second array is built from the difference between every third item in the array starting at
        # two and every third item in the array starting at zero. The cross operation then returns an array of
        # the normals of each set of three vertices.
        n = numpy.cross(self._vertices[1::3] - self._vertices[::3], self._vertices[2::3] - self._vertices[::3])

        # We then calculate the length for each normal and perform normalization on the normals.
        l = numpy.linalg.norm(n, axis=1)
        n[:, 0] /= l
        n[:, 1] /= l
        n[:, 2] /= l

        # Finally, we store the normals per vertex, with each face normal being repeated three times, once for
        # every vertex.
        self._normals = n.repeat(3, axis=0)
