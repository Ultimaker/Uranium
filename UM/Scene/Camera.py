# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import SceneNode

from UM.Logger import Logger
from UM.Math.Matrix import Matrix
from UM.Math.Ray import Ray
from UM.Math.Vector import Vector

import enum
import numpy
import numpy.linalg
from typing import cast, Dict, Optional, Tuple, TYPE_CHECKING
from UM.Signal import Signal

if TYPE_CHECKING:
    from UM.Mesh.MeshData import MeshData


class Camera(SceneNode.SceneNode):
    """A SceneNode subclass that provides a camera object.

    The camera provides a projection matrix and its transformation matrix
    can be used as view matrix.
    """

    class PerspectiveMode(enum.Enum):
        PERSPECTIVE = "perspective"
        ORTHOGRAPHIC = "orthographic"

    @staticmethod
    def getDefaultZoomFactor() -> float:
        return -0.3334

    def __init__(self, name: str = "", parent: Optional[SceneNode.SceneNode] = None) -> None:
        super().__init__(parent)
        self._name = name  # type: str
        self._projection_matrix = Matrix()  # type: Matrix
        self._projection_matrix.setOrtho(-5, 5, -5, 5, -100, 100)
        self._perspective = True  # type: bool
        self._viewport_width = 0  # type: int
        self._viewport_height = 0  # type: int
        self._window_width = 0  # type: int
        self._window_height = 0  # type: int
        self._auto_adjust_view_port_size = True  # type: bool
        self.setCalculateBoundingBox(False)
        self._cached_view_projection_matrix = None  # type: Optional[Matrix]
        self._camera_light_position = None
        self._cached_inversed_world_transformation = None
        self._zoom_factor = Camera.getDefaultZoomFactor()

        from UM.Application import Application
        Application.getInstance().getPreferences().addPreference("general/camera_perspective_mode", default_value = self.PerspectiveMode.PERSPECTIVE.value)
        Application.getInstance().getPreferences().preferenceChanged.connect(self._preferencesChanged)
        self._preferencesChanged("general/camera_perspective_mode")

    def __deepcopy__(self, memo: Dict[int, object]) -> "Camera":
        copy = cast(Camera, super().__deepcopy__(memo))
        copy._projection_matrix = self._projection_matrix
        copy._window_height = self._window_height
        copy._window_width = self._window_width
        copy._viewport_height = self._viewport_height
        copy._viewport_width = self._viewport_width
        return copy

    def getZoomFactor(self):
        return self._zoom_factor

    def setZoomFactor(self, zoom_factor: float) -> None:
        # Only an orthographic camera has a zoom at the moment.
        if not self.isPerspective():
            if self._zoom_factor != zoom_factor:
                self._zoom_factor = zoom_factor
                self._updatePerspectiveMatrix()

    def setMeshData(self, mesh_data: Optional["MeshData"]) -> None:
        assert mesh_data is None, "Camera's can't have mesh data"

    def getAutoAdjustViewPort(self) -> bool:
        return self._auto_adjust_view_port_size

    def setAutoAdjustViewPort(self, auto_adjust: bool) -> None:
        self._auto_adjust_view_port_size = auto_adjust

    def getProjectionMatrix(self) -> Matrix:
        """Get the projection matrix of this camera."""

        return self._projection_matrix

    def getViewportWidth(self) -> int:
        return self._viewport_width

    def setViewportWidth(self, width: int) -> None:
        self._viewport_width = width
        self._updatePerspectiveMatrix()

    def setViewportHeight(self, height: int) -> None:
        self._viewport_height = height
        self._updatePerspectiveMatrix()

    def setViewportSize(self, width: int, height: int) -> None:
        self._viewport_width = width
        self._viewport_height = height
        self._updatePerspectiveMatrix()

    def _updatePerspectiveMatrix(self) -> None:
        view_width = self._viewport_width
        view_height = self._viewport_height
        projection_matrix = Matrix()
        if self.isPerspective():
            if view_width != 0 and view_height != 0:
                projection_matrix.setPerspective(30, view_width / view_height, 1, 500)
        else:
            # Almost no near/far plane, please.
            if view_width != 0 and view_height != 0:
                horizontal_zoom = view_width * self._zoom_factor
                vertical_zoom = view_height * self._zoom_factor
                projection_matrix.setOrtho(-view_width / 2 - horizontal_zoom, view_width / 2 + horizontal_zoom,
                                           -view_height / 2 - vertical_zoom, view_height / 2 + vertical_zoom,
                                           -9001, 9001)
        self.setProjectionMatrix(projection_matrix)
        self.perspectiveChanged.emit(self)

    def getViewProjectionMatrix(self) -> Matrix:
        if self._cached_view_projection_matrix is None:
            inverted_transformation = self.getWorldTransformation()
            inverted_transformation.invert()
            self._cached_view_projection_matrix = self._projection_matrix.multiply(inverted_transformation, copy = True)
        return self._cached_view_projection_matrix

    def _updateWorldTransformation(self) -> None:
        self._cached_view_projection_matrix = None
        self._cached_inversed_world_transformation = None
        self._camera_light_position = None
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

    def setProjectionMatrix(self, matrix: Matrix) -> None:
        """Set the projection matrix of this camera.
        :param matrix: The projection matrix to use for this camera.
        """

        self._projection_matrix = matrix
        self._cached_view_projection_matrix = None

    def getInverseWorldTransformation(self):
        if self._cached_inversed_world_transformation is None:
            self._cached_inversed_world_transformation = self.getWorldTransformation()
            self._cached_inversed_world_transformation.invert()
        return self._cached_inversed_world_transformation

    def getCameraLightPosition(self):
        if self._camera_light_position is None:
            self._camera_light_position = self.getWorldPosition() + Vector(0, 50, 0)
        return self._camera_light_position

    def isPerspective(self) -> bool:
        return self._perspective

    def setPerspective(self, perspective: bool) -> None:
        if self._perspective != perspective:
            self._perspective = perspective
            self._updatePerspectiveMatrix()

    perspectiveChanged = Signal()

    def getRay(self, x: float, y: float) -> Ray:
        """Get a ray from the camera into the world.

        This will create a ray from the camera's origin, passing through (x, y)
        on the near plane and continuing based on the projection matrix.

        :param x: The X coordinate on the near plane this ray should pass through.
        :param y: The Y coordinate on the near plane this ray should pass through.

        :return: A Ray object representing a ray from the camera origin through X, Y.

        :note The near-plane coordinates should be in normalized form, that is within (-1, 1).
        """

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

        if self.isPerspective():
            origin = self.getWorldPosition()
            direction = -direction
        else:
            # In orthographic mode, the origin is the click position on the plane where the camera resides, and that
            # plane is parallel to the near and the far planes.
            projection = numpy.array([view_x, -view_y, 0.0, 1.0], dtype = numpy.float32)
            projection = numpy.dot(inverted_projection, projection)
            projection = numpy.dot(transformation, projection)
            projection = projection[0:3] / projection[3]

            origin = Vector(data = projection)

        return Ray(origin, Vector(direction[0], direction[1], direction[2]))

    def project(self, position: Vector) -> Tuple[float, float]:
        """Project a 3D position onto the 2D view plane."""

        projection = self._projection_matrix
        view = self.getWorldTransformation()
        view.invert()

        position = position.preMultiply(view)
        position = position.preMultiply(projection)
        return position.x / position.z / 2.0, position.y / position.z / 2.0

    def _preferencesChanged(self, key: str) -> None:
        """Updates the _perspective field if the preference was modified."""

        if key != "general/camera_perspective_mode":  # Only listen to camera_perspective_mode.
            return
        from UM.Application import Application
        new_mode = str(Application.getInstance().getPreferences().getValue("general/camera_perspective_mode"))

        # Translate the selected mode to the camera state.
        if new_mode == str(self.PerspectiveMode.ORTHOGRAPHIC.value):
            Logger.log("d", "Changing perspective mode to orthographic.")
            self.setPerspective(False)
        elif new_mode == str(self.PerspectiveMode.PERSPECTIVE.value):
            Logger.log("d", "Changing perspective mode to perspective.")
            self.setPerspective(True)
        else:
            Logger.log("w", "Unknown perspective mode {new_mode}".format(new_mode = new_mode))
