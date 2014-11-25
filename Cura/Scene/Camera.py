from . import SceneNode

from Cura.Math.Matrix import Matrix

##  A SceneNode subclass that provides a camera object.
#   The camera provides a projection matrix and its transformation matrix
#   can be used as view matrix.
class Camera(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._projectionMatrix = Matrix()
        self._projectionMatrix.setOrtho(-5, 5, 5, -5, -100, 100)
        #self._projectionMatrix.setPerspective(45, 1, 0, 5)
        self._locked = False

    ##  Get the projection matrix of this camera.
    def getProjectionMatrix(self):
        return self._projectionMatrix

    ##  Set the projection matrix of this camera.
    #   \param matrix The projection matrix to use for this camera.
    def setProjectionMatrix(self, matrix):
        self._projectionMatrix = matrix
