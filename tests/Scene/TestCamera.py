import numpy
import pytest

from UM.Math.Matrix import Matrix
from UM.Mesh.MeshData import MeshData
from UM.Scene.Camera import Camera


def test_setMeshData():
    camera = Camera()
    with pytest.raises(AssertionError):
        camera.setMeshData(MeshData())

    # This is allowed
    camera.setMeshData(None)

def test_getterAndSetters():
    # Pretty much all of them are super simple, but it doesn't hurt to check them.
    camera = Camera()

    camera.setAutoAdjustViewPort(False)
    assert camera.getAutoAdjustViewPort() == False

    camera.setViewportWidth(12)
    assert camera.getViewportWidth() == 12

    camera.setViewportHeight(12)
    assert camera.getViewportHeight() == 12

    camera.setViewportSize(22, 22)
    assert camera.getViewportHeight() == 22
    assert camera.getViewportWidth() == 22

    camera.setWindowSize(9001, 9002)
    assert camera.getWindowSize() == (9001, 9002)

    camera.setPerspective(False)
    assert camera.isPerspective() == False

    matrix = Matrix()
    matrix.setPerspective(10, 20, 30, 40)
    camera.setProjectionMatrix(matrix)

    assert numpy.array_equal(camera.getProjectionMatrix().getData(), matrix.getData())
