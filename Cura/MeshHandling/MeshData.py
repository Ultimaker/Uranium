from Cura.MeshHandling.Vertex import Vertex
from Cura.Math.Vector import Vector

import numpy
# Class to hold a list of verts and possibly how (and if) they are connected.
class MeshData(object):
    def __init__(self):
        self._verts = None
        self._num_verts = 0
        
    def getVerts(self):
        return self._verts
    
    def getNumVerts(self):
        return self._num_verts

    ## Get a vertex by index
    def getVertex(self, index):
        try:
            return self._verts[index]
        except IndexError:
            return None
    
    ## Transform the meshdata by given Matrix
    def transform(self, transformation):
        #TODO: Implement
        pass
    
    ## Set the amount of faces before loading data to the mesh. This way we can create the array before we fill it.
    # \param num_faces Number of faces for which memory must be reserved.
    def reserveFaceCount(self, num_faces):
        # Create an array of (num_faces * 3) Vertex objects
        self._verts = [Vertex() for v in xrange(num_faces * 3)]
        self._num_verts = 0
    
    ## Set the amount of verts before loading data to the mesh. This way we can create the array before we fill it.
    # \param num_verts Number of verts to be reserved.
    def reserveVertexCount(self, num_verts):
        # Create an array of num_verts Vertex objects
        self._verts = [Vertex() for v in xrange(num_verts)]
        self._num_verts = 0
    
    ## Add a vertex to the mesh.
    # \param x x coordinate of vertex.
    # \param y y coordinate of vertex.
    # \param z z coordinate of vertex.
    def addVertex(self,x,y,z):
        if len(self._verts) == self._num_verts:
            self._verts.append(Vertex())

        self._verts[self._num_verts].setPosition(Vector(x, y, z))
        self._num_verts += 1
    
    ## Add a vertex to the mesh.
    # \param x x coordinate of vertex.
    # \param y y coordinate of vertex.
    # \param z z coordinate of vertex.
    # \param nx x part of normal.
    # \param ny y part of normal.
    # \param nz z part of normal.
    def addVertexWithNormal(self,x,y,z,nx,ny,nz):
        if len(self._verts) == self._num_verts:
            self._verts.append(Vertex())

        self._verts[self._num_verts].setPosition(Vector(x, y, z))
        self._verts[self._num_verts].setNormal(Vector(nx, ny, nz))
        self._num_verts += 1
    
    ## Add a face by providing three verts.
    # \param x0 x coordinate of first vertex.
    # \param y0 y coordinate of first vertex.
    # \param z0 z coordinate of first vertex.
    # \param x1 x coordinate of second vertex.
    # \param y1 y coordinate of second vertex.
    # \param z1 z coordinate of second vertex.
    # \param x2 x coordinate of third vertex.
    # \param y2 y coordinate of third vertex.
    # \param z2 z coordinate of third vertex.
    def addFace(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
        self.addVertex(x0, y0, z0)
        self.addVertex(x1, y1, z1)
        self.addVertex(x2, y2, z2)
        
    ## Calculate the normals of this mesh, assuming it was created by using addFace (eg; the verts are connected)    
    def calculateNormals(self):
        pass
        #TODO: Port this code to using Vertex objects
        #vertex_data = self._verts.reshape(self._num_verts / 3, 6, 3)
        #normals = numpy.cross(vertex_data[::, 2] - vertex_data[::, 0], vertex_data[::, 4] - vertex_data[::, 0])
        #length = numpy.sqrt(normals[:, 0] ** 2 + normals[:, 1] ** 2 + normals[:, 2] ** 2)

        #normals[:, 0] /= length
        #normals[:, 1] /= length
        #normals[:, 2] /= length

        #vertex_data[::, 1] = normals
        #vertex_data[::, 3] = normals
        #vertex_data[::, 5] = normals
        
