# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import SceneNode

from UM.Math.Matrix import Matrix
from UM.Math.Ray import Ray
from UM.Math.Vector import Vector

import copy
import numpy
import numpy.linalg
from typing import cast, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from UM.Mesh.MeshData import MeshData


##  A SceneNode subclass that provides a camera object.
#
#   The camera provides a projection matrix and its transformation matrix
#   can be used as view matrix.
class Camera(SceneNode.SceneNode):
    def __init__(self, name: str = "", parent: SceneNode.SceneNode = None) -> None:
        super().__init__(parent)
        self._name = name  # type: str
        self._projection_matrix = Matrix()  # type: Matrix
        self._projection_matrix.setOrtho(-5, 5, 5, -5, -100, 100)
        self._perspective = True  # type: bool
        self._viewport_width = 0  # type: int
        self._viewport_height = 0  # type: int
        self._window_width = 0  # type: int
        self._window_height = 0  # type: int
        self._auto_adjust_view_port_size = True  # type: bool
        self.setCalculateBoundingBox(False)
        self._cached_view_projection_matrix = None # type: Optional[Matrix]

    def __deepcopy__(self, memo: Dict[int, object]) -> "Camera":
        copy = cast(Camera, super().__deepcopy__(memo))
        copy._projection_matrix = self._projection_matrix
        copy._window_height = self._window_height
        copy._window_width = self._window_width
        copy._viewport_height = self._viewport_height
        copy._viewport_width = self._viewport_width
        return copy

    def setMeshData(self, mesh_data: Optional["MeshData"]) -> None:
        assert mesh_data is None, "Camera's can't have mesh data"

    def getAutoAdjustViewPort(self) -> bool:
        return self._auto_adjust_view_port_size

    def setAutoAdjustViewPort(self, auto_adjust: bool) -> None:
        self._auto_adjust_view_port_size = auto_adjust

    ##  Get the projection matrix of this camera.
    def getProjectionMatrix(self) -> Matrix:
        return self._projection_matrix
    
    def getViewportWidth(self) -> int:
        return self._viewport_width
    
    def setViewportWidth(self, width: int) -> None:
        self._viewport_width = width
    
    def setViewportHeight(self, height: int) -> None:
        self._viewport_height = height
        
    def setViewportSize(self, width: int, height: int) -> None:
        self._viewport_width = width
        self._viewport_height = height

    def getViewProjectionMatrix(self):
        if self._cached_view_projection_matrix is None:
            inverted_transformation = self.getWorldTransformation()
            inverted_transformation.invert()
            self._cached_view_projection_matrix = self._projection_matrix.multiply(inverted_transformation, copy = True)
        return self._cached_view_projection_matrix

    def _updateWorldTransformation(self):
        self._cached_view_projection_matrix = None
        super()._updateWorldTransformation()
    
    def getViewportHeight(self) -> int:
        return self._viewport_height

    def setWindowSize(self, width: int, height: int) -> None:
        self._window_width = width
        self._window_height = height

    def getWindowSize(self) -> Tuple[int, int]:
        return self._window_width, self._window_height

    def render(self, renderer) -> bool:
        # It's a camera. It doesn't need rendering. 
        return True
    
    ##  Set the projection matrix of this camera.
    #   \param matrix The projection matrix to use for this camera.
    def setProjectionMatrix(self, matrix: Matrix) -> None:
        self._projection_matrix = matrix
        self._cached_view_projection_matrix = None

    def isPerspective(self) -> bool:
        return self._perspective

    def setPerspective(self, perspective: bool) -> None:
        self._perspective = perspective

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
    def getRay(self, x: float, y: float) -> Ray:
        window_x = ((x + 1) / 2) * self._window_width
        window_y = ((y + 1) / 2) * self._window_height
        view_x = (window_x / self._viewport_width) * 2 - 1
        view_y = (window_y / self._viewport_height) * 2 - 1

        inverted_projection = numpy.linalg.inv(self._projection_matrix.getData().copy())
        transformation = self.getWorldTransformation().getData()

        near = numpy.array([view_x, -view_y, -1.0, 1.0], dtype = numpy.float32)
        near = numpy.dot(inverted_projection, near)
        near = numpy.dot(transformation, near)
        near = near[0:3] / near[3]

        far = numpy.array([view_x, -view_y, 1.0, 1.0], dtype = numpy.float32)
        far = numpy.dot(inverted_projection, far)
        far = numpy.dot(transformation, far)
        far = far[0:3] / far[3]

        direction = far - near
        direction /= numpy.linalg.norm(direction)

        return Ray(self.getWorldPosition(), Vector(-direction[0], -direction[1], -direction[2]))

    ##  Project a 3D position onto the 2D view plane.
    def project(self, position: Vector) -> Tuple[float, float]:
        projection = self._projection_matrix
        view = self.getWorldTransformation()
        view.invert()

        position = position.preMultiply(view)
        position = position.preMultiply(projection)
        return position.x / position.z / 2.0, position.y / position.z / 2.0
