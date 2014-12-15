from . import SceneNode

from UM.Math.Matrix import Matrix

import numpy

##  A SceneNode subclass that provides a camera object.
#
#   The camera provides a projection matrix and its transformation matrix
#   can be used as view matrix.
class Camera(SceneNode.SceneNode):
    def __init__(self, name, parent = None):
        super().__init__(parent)
        self._name = name
        self._projectionMatrix = Matrix()
        self._projectionMatrix.setOrtho(-5, 5, 5, -5, -100, 100)
        self._perspective = False
        #self._projectionMatrix.setPerspective(45, 1, 0, 5)

    def getName(self):
        return self._name

    ##  Get the projection matrix of this camera.
    def getProjectionMatrix(self):
        return self._projectionMatrix

    ##  Set the projection matrix of this camera.
    #   \param matrix The projection matrix to use for this camera.
    def setProjectionMatrix(self, matrix):
        self._projectionMatrix = matrix

    def isPerspective(self):
        return self._perspective

    def setPerspective(self, pers):
        self._perspective = pers

    def lookAt(self, center, up):
        eye = self.getPosition()
        f = (center - eye).normalize()
        up.normalize()
        s = f.cross(up).normalize()
        u = s.cross(f).normalize()

        m = Matrix(numpy.array([
            [ s.x,  u.x, -f.x, eye.x],
            [ s.y,  u.y, -f.y, eye.y],
            [ s.z,  u.z, -f.z, eye.z],
            [ 0.0,  0.0,  0.0,   1.0]],
            dtype=numpy.float32))

        self.setLocalTransformation(m)
        #self.translate(eye)
