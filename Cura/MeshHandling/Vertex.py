from Cura.Math.Vector import Vector

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
        self._normal = Vector()

        if len(args) == 3:
            self._position = Vector(args[0], args[1], args[2])

        if "position" in kwargs:
            self._position = kwargs["position"]

        if "normal" in kwargs:
            self._normal = kwargs["normal"]

    def getPosition(self):
        return self._position

    def setPosition(self, position):
        self._position = position

    def getNormal(self):
        return self._normal

    def setNormal(self, normal):
        self._normal = normal
