from . import SceneObject

from Cura.Math.Matrix import Matrix

class Camera(SceneObject.SceneObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._projectionMatrix = Matrix()
        self._projectionMatrix.setOrtho(-5, 5, 5, -5, -100, 100)
        #self._projectionMatrix.setPerspective(45, 1, 0, 5)
        self._locked = False

    def getProjectionMatrix(self):
        return self._projectionMatrix

    def setProjectionMatrix(self, matrix):
        self._projectionMatrix = matrix

    def isLocked(self):
        return self._locked

    def setLocked(self, lock):
        self._locked = lock
