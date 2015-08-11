# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import SceneNode

from UM.Math.Matrix import Matrix
from UM.Math.Ray import Ray
from UM.Math.Vector import Vector

import numpy
import numpy.linalg

##  A SceneNode subclass that provides a camera object.
#
#   The camera provides a projection matrix and its transformation matrix
#   can be used as view matrix.
class Camera(SceneNode.SceneNode):
    def __init__(self, name, parent = None):
        super().__init__(parent)
        self._name = name
        self._projection_matrix = Matrix()
        self._projection_matrix.setOrtho(-5, 5, 5, -5, -100, 100)
        self._perspective = False
        self._viewport_width = 0
        self._viewport_height = 0

        self.setCalculateBoundingBox(False)

    ##  Get the projection matrix of this camera.
    def getProjectionMatrix(self):
        return self._projection_matrix
    
    def getViewportWidth(self):
        return self._viewport_width
    
    def setViewportWidth(self, width):
        self._viewport_width = width
    
    def setViewPortHeight(self,height):
        self._viewport_height = height
        
    def setViewportSize(self,width,height):
        self._viewport_width = width
        self._viewport_height = height
    
    def getViewportHeight(self):
        return self._viewport_height
    
    ##  Set the projection matrix of this camera.
    #   \param matrix The projection matrix to use for this camera.
    def setProjectionMatrix(self, matrix):
        self._projection_matrix = matrix

    def isPerspective(self):
        return self._perspective

    def setPerspective(self, pers):
        self._perspective = pers

    ##  Get a ray from the camera into the world.
    #
    #   This will create a ray from the camera's origin, passing through (x, y)
    #   on the near plane and continuing based on the projection matrix.
    #
    #   \param x The X coordinate on the near plane this ray should pass through.
    #   \param y The Y coordinate on the near plane this ray should pass through.
    #
    #   \return A Ray object representing a ray from the camera origin through X, Y.
    #
    #   \note The near-plane coordinates should be in normalized form, that is within (-1, 1).
    def getRay(self, x, y):
        invp = numpy.linalg.inv(self._projection_matrix.getData().copy())
        invv = self.getWorldTransformation().getData()

        near = numpy.array([x, -y, -1.0, 1.0], dtype=numpy.float32)
        near = numpy.dot(invp, near)
        near = numpy.dot(invv, near)
        near = near[0:3] / near[3]

        far = numpy.array([x, -y, 1.0, 1.0], dtype = numpy.float32)
        far = numpy.dot(invp, far)
        far = numpy.dot(invv, far)
        far = far[0:3] / far[3]

        dir = far - near
        dir /= numpy.linalg.norm(dir)

        return Ray(self.getWorldPosition(), Vector(-dir[0], -dir[1], -dir[2]))

    ##  Project a 3D position onto the 2D view plane.
    def project(self, position):
        projection = self._projection_matrix
        view = self.getWorldTransformation().getInverse()

        position = position.preMultiply(view)
        position = position.preMultiply(projection)

        return (position.x, position.y)
