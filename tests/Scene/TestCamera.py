import numpy
import pytest

from UM.Math.Matrix import Matrix
from UM.Math.Ray import Ray
from UM.Math.Vector import Vector
from UM.Mesh.MeshData import MeshData
from UM.Scene.Camera import Camera

from unittest.mock import MagicMock, patch

from copy import deepcopy

@pytest.fixture
def camera():
    with patch("UM.Application.Application.getInstance", MagicMock()):
        return Camera()

def test_setMeshData(camera):
    with pytest.raises(AssertionError):
        camera.setMeshData(MeshData())

    # This is allowed
    camera.setMeshData(None)

def test_getterAndSetters(camera):
    # Pretty much all of them are super simple, but it doesn't hurt to check them.

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

    camera.setZoomFactor(1)
    assert camera.getZoomFactor() == 1

    assert camera.render(None)  # Should always be true, as it's a camera


def test_deepCopy(camera):
    camera.setWindowSize(100, 200)
    camera.setViewportSize(300, 400)

    copied_camera = deepcopy(camera)

    assert copied_camera.getWindowSize() == (100, 200)
    assert copied_camera.getViewportHeight() == 400
    assert copied_camera.getViewportWidth() == 300


@pytest.mark.parametrize("coordinates,direction", [((0, 0), (0.0, 0.0, -1.0)),
                        ((50, 50), (0.7061278820037842, -0.7061278820037842, -0.0526)),
                        ((100, 100), (0.706861674785614, -0.706861674785614, -0.026327675208449364)),
                        ((42, 8), (0.9786322116851807, -0.18640615046024323, -0.08678573369979858))])
def test_getRayPerspective(coordinates, direction, camera):
    camera.setViewportSize(100, 100)
    camera.setWindowSize(100, 100)
    result_ray = camera.getRay(coordinates[0], coordinates[1])
    assert result_ray.direction == Vector(direction[0], direction[1], direction[2])

@pytest.mark.parametrize("coordinates,direction", [((0, 0), (0.0, 0.0, -1.0)),
                                                   ((50, 50), (0.0, 0.0, -1.0)),
                                                   ((100, 100), (0.0, 0.0, -1.0)),
                                                   ((42, 8), (0.0, 0.0, -1.0))])
def test_getRayOrthographic(coordinates, direction, camera):
    camera.isPerspective = MagicMock(return_value = False)
    camera.setViewportSize(100, 100)
    camera.setWindowSize(100, 100)
    result_ray = camera.getRay(coordinates[0], coordinates[1])
    assert result_ray.direction == Vector(direction[0], direction[1], direction[2])


def test_project(camera):
    assert camera.project(Vector(10, 10, 10)) == (-10.000000372529039, -10.000000372529039)


def test_getViewProjectionMatrix(camera):
    assert camera.getViewProjectionMatrix() == Matrix([[0.2, 0, 0, 0],
                                                      [0, 0.2, 0, 0],
                                                      [0, 0, -0.01, 0],
                                                      [0, 0, 0, 1]])