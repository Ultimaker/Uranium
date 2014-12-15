from UM.Math.Vector import Vector
import numpy

##  A vertex with a position and a normal.

class Vertex(object):
    ##  Construct a vertex.
    #
    #   Possible keyword parameters:
    #   - position: Vector with the vertex' position.
    #   - normal: Vector with the vertex' normal
    #
    #   Unnamed arguments:
    #   - x, y, z passed as numbers.
    def __init__(self, *args, **kwargs):
        self._position = Vector()
        self._normal = None

        if len(args) == 3:
            self._position = Vector(args[0], args[1], args[2])

        if "position" in kwargs:
            self._position = kwargs["position"]

        if "normal" in kwargs:
            self._normal = kwargs["normal"]

    ##  Get the position the vertex
    #   \returns position Vector
    @property
    def position(self):
        return self._position

    ##  Set the position the vertex
    #   \param position Vector
    def setPosition(self, position):
        self._position = position
    
    ##  Get the normal the vertex
    #   \returns normal Vector
    @property
    def normal(self):
        return self._normal
    
    ##  Set the normal the vertex
    #   \param normal Vector
    def setNormal(self, normal):
        self._normal = normal

    def hasNormal(self):
        return self._normal != None
    
    ##  Convert the vertex into a string, which is required for parsing over sockets / streams
    #   It's kinda hackish to do it this way, but it would take to much effort to implement myself.
    def toString(self):
        return numpy.array([self._position.x(),self._position.y(),self._position.z(),self._normal.x(),self._normal.y(),self._normal.z()]).tostring()
