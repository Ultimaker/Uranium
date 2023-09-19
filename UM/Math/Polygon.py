# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional, Tuple, List, Union

import numpy
import math
import pyclipper
import scipy.spatial

from UM.Logger import Logger
from UM.Math import NumPyUtil

class Polygon:
    """A class representing an immutable arbitrary 2-dimensional polygon."""

    CLIPPER_PRECISION = 1000
    """
    Number of units per mm to use in clipper operations.
    """

    @staticmethod
    def approximatedCircle(radius, num_segments = 8):
        """Return vertices from an approximate circle.

        An octagon is returned, which comes close enough to a circle.

        :param radius: The radius of the circle.
        :return: A polygon that approximates a circle.
        """

        step = 2 * math.pi / num_segments

        points = []
        for i in range(0, num_segments):
            points.append([radius * -math.cos(i * step), radius * math.sin(i * step)])

        return Polygon(points = numpy.array(points, numpy.float32))

    @staticmethod
    def _fromClipperPoints(points: numpy.ndarray) -> "Polygon":
        """
        Converts the clipper point representation into a normal polygon.
        :param points: The clipper
        :return:
        """
        return Polygon(points = points.astype(numpy.float32) / Polygon.CLIPPER_PRECISION)

    def __init__(self, points: Optional[Union[numpy.ndarray, List]] = None):
        if points is not None:
            self._points = NumPyUtil.immutableNDArray(points)
        else:
            self._points = NumPyUtil.immutableNDArray([])

    def __eq__(self, other):
        if self is other:
            return True
        if type(other) is not Polygon:
            return False

        point_count = len(self._points) if self._points is not None else 0
        point_count2 = len(other.getPoints()) if other.getPoints() is not None else 0
        if point_count != point_count2:
            return False
        return numpy.array_equal(self._points, other.getPoints())

    def __repr__(self):
        """Gives a debugging representation of the polygon.

        This lists the polygon's coordinates, like so::
        [[0,0], [1,3], [3,0]]

        :return: A representation of the polygon that is useful for debugging.
        """

        coordinates = (("[" + str(point[0]) + "," + str(point[1]) + "]") for point in self._points)
        return "[" + ", ".join(coordinates) + "]"

    def isValid(self) -> bool:
        return bool(self._points is not None and len(self._points) >= 3)

    def getPoints(self) -> numpy.ndarray:
        return self._points

    def project(self, normal) -> Tuple[float, float]:
        """Project this polygon on a line described by a normal.

        :param normal: The normal to project on.
        :return: A tuple describing the line segment of this Polygon projected on to the infinite line described by normal.
        The first element is the minimum value, the second the maximum.
        """

        projection_min = numpy.dot(normal, self._points[0])

        projection_max = projection_min
        for point in self._points:
            projection = numpy.dot(normal, point)
            projection_min = min(projection_min, projection)
            projection_max = max(projection_max, projection)

        return projection_min, projection_max

    def translate(self, x: float = 0, y: float = 0) -> "Polygon":
        """Moves the polygon by a fixed offset.

        :param x: The distance to move along the X-axis.
        :param y: The distance to move along the Y-axis.
        """

        if self.isValid():
            return Polygon(numpy.add(self._points, numpy.array([[x, y]])))
        else:
            return self

    def mirror(self, point_on_axis: List[float], axis_direction: List[float]) -> "Polygon":
        """Mirrors this polygon across the specified axis.

        :param point_on_axis: A point on the axis to mirror across.
        :param axis_direction: The direction vector of the axis to mirror across.
        """

        # Input checking.
        if axis_direction == [0, 0]:
            Logger.log("w", "Tried to mirror a polygon over an axis with direction [0, 0].")
            return self  # Axis has no direction. Can't expect us to mirror anything!
        axis_direction /= numpy.linalg.norm(axis_direction)  # Normalise the direction.
        if not self.isValid():  # Not a valid polygon, so don't do anything.
            return self

        # In order to be able to mirror points around an arbitrary axis, we have to normalize the axis and all points
        # such that the axis goes through the origin.
        point_matrix = numpy.matrix(self._points)  # type: ignore
        # Moves all points such that the axis origin is at [0,0].
        point_matrix -= point_on_axis  # type: ignore

        # To mirror a coordinate, we have to add the projection of the point to the axis twice
        # (where v is the vector to reflect):
        #  reflection(v) = 2 * projection(v) - v
        # Writing out the projection, this becomes (where l is the normalised direction of the line):
        #  reflection(v) = 2 * (l . v) l - v
        # With Snell's law this can be simplified to the Householder transformation matrix:
        #  reflection(v) = R v
        #  R = 2 l l^T - I
        # This simplifies the entire reflection to one big matrix transformation.
        axis_matrix = numpy.matrix(axis_direction) # type: ignore
        reflection = 2 * numpy.transpose(axis_matrix) * axis_matrix - numpy.identity(2)
        point_matrix = point_matrix * reflection  # Apply the actual transformation.

        # Shift the points back to the original coordinate space before the axis was normalised to the origin.
        point_matrix += point_on_axis # type: ignore
        return Polygon(point_matrix.getA()[::-1])

    def scale(self, factor: float, origin: Optional[List[float]] = None) -> "Polygon":
        """
        Scales this polygon around a certain origin point.
        :param factor: The scaling factor.
        :param origin: Origin point around which to scale, 2D. As the scale
        factor approaches 0, all coordinates will approach this origin point. As
        the scale factor grows, all coordinates will move away from this origin
        point. If `None`, the 0,0 coordinate will be used.
        :return: A transformed polygon.
        """
        if not self.isValid():
            return self

        if origin is None:
            origin = [0, 0]

        transformation = numpy.identity(3) * factor  # Just the scaling matrix.
        delta_scale = factor - 1
        transformation[2][0] = delta_scale * -origin[0]
        transformation[2][1] = delta_scale * -origin[1]

        # Apply that affine transformation to the point data.
        point_data = numpy.lib.pad(self._points, ((0, 0), (0, 1)), "constant", constant_values = (1))  # Turn 3D to do an affine transformation.
        point_data = point_data.dot(transformation)

        return Polygon(point_data[:, :-1])  # Leave out the affine component.

    def intersectionConvexHulls(self, other: "Polygon") -> "Polygon":
        """Computes the intersection of the convex hulls of this and another
        polygon.

        :param other: The other polygon to intersect convex hulls with.
        :return: The intersection of the two polygons' convex hulls.
        """
        me = self.getConvexHull()
        him = other.getConvexHull()

        # If either polygon has no surface area, then the intersection is empty.
        if len(me.getPoints()) <= 2 or len(him.getPoints()) <= 2:
            return Polygon()

        clipper = pyclipper.Pyclipper()
        clipper.AddPath(me._clipperPoints(), pyclipper.PT_SUBJECT, closed = True)
        clipper.AddPath(other._clipperPoints(), pyclipper.PT_CLIP, closed = True)

        points = clipper.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
        if len(points) == 0:
            return Polygon()
        points = points[0]  # Intersection between convex hulls should result in a single (convex) simple polygon. Take just the one polygon.
        if points[0] == points[-1]:  # Represent closed polygons without closing vertex.
            points.pop()
        return self._fromClipperPoints(numpy.array(points))

    #  Computes the convex hull of the union of the convex hulls of this and another polygon.
    #
    #   \param other The other polygon to combine convex hulls with.
    #   \return The convex hull of the union of the two polygons' convex hulls.
    def unionConvexHulls(self, other: "Polygon") -> "Polygon":
        if len(self.getPoints()) == 0: # Concatenate doesn't deal well with empty arrays (since they are not the same dimension), so catch that case first.
            return other
        if len(other.getPoints()) == 0:
            return self
        # Combine all points and take the convex hull of that.
        all_points = numpy.concatenate((self.getPoints(), other.getPoints()))
        combined_polys = Polygon(all_points)
        return combined_polys.getConvexHull()

    def intersectsPolygon(self, other: "Polygon") -> Optional[Tuple[float, float]]:
        """Check to see whether this polygon intersects with another polygon.

        :param other: :type{Polygon} The polygon to check for intersection.
        :return: A tuple of the x and y distance of intersection, or None if no intersection occurred.
        """
        if not self.isValid() or not other.isValid():
            return None

        clipper = pyclipper.Pyclipper()
        try:
            clipper.AddPath(self._clipperPoints(), pyclipper.PT_SUBJECT, closed = True)
            clipper.AddPath(other._clipperPoints(), pyclipper.PT_CLIP, closed = True)
            intersection_points = clipper.Execute(pyclipper.CT_INTERSECTION)
        except pyclipper.ClipperException:
            # Invalid geometry, such as a zero-area polygon.
            return None

        if len(intersection_points) == 0:
            return None

        # Find the bounds of the intersection area.
        mini = (math.inf, math.inf)
        maxi = (-math.inf, -math.inf)
        for poly in intersection_points:  # Each simple polygon in the complex intersection multi-polygon.
            for vertex in poly:
                mini = (min(mini[0], vertex[0]), min(mini[1], vertex[1]))
                maxi = (max(maxi[0], vertex[0]), max(maxi[1], vertex[1]))
        return float(maxi[0] - mini[0]) / self.CLIPPER_PRECISION, float(maxi[1] - mini[1]) / self.CLIPPER_PRECISION

    def getConvexHull(self) -> "Polygon":
        """Calculate the convex hull around the set of points of this polygon.

        :return: The convex hull around the points of this polygon.
        """

        points = self._points

        if len(points) < 1:
            return Polygon(numpy.zeros((0, 2), numpy.float64))
        if len(points) <= 2:
            return Polygon(numpy.array(points, numpy.float64))

        try:
            hull = scipy.spatial.ConvexHull(points)
        except scipy.spatial.qhull.QhullError:
            return Polygon(numpy.zeros((0, 2), numpy.float64))
        except OSError:  # For some reason, Spatial sometimes attempts to open a temp file. If this temp file contains non-ASCII characters that fails. See https://github.com/scipy/scipy/issues/8850
            return Polygon(numpy.zeros((0, 2), numpy.float64))

        return Polygon(numpy.flipud(hull.points[hull.vertices]))

    def getMinkowskiSum(self, other: "Polygon") -> "Polygon":
        """Perform a Minkowski sum of this polygon with another polygon.

        :param other: The polygon to perform a Minkowski sum with.
        :return: :type{Polygon} The Minkowski sum of this polygon with other.
        """
        if len(self._points) == 0 or len(other._points) == 0:  # Summing an empty polygon with a certain kernel, or summing a normal polygon with an empty polygon, would crash Numpy down below.
            return Polygon(self._points)
        points = numpy.zeros((len(self._points) * len(other._points), 2))
        for n in range(0, len(self._points)):
            for m in range(0, len(other._points)):
                points[n * len(other._points) + m] = self._points[n] + other._points[m]

        return Polygon(points)

    def getMinkowskiHull(self, other: "Polygon") -> "Polygon":
        """Create a Minkowski hull from this polygon and another polygon.

        The Minkowski hull is the convex hull around the Minkowski sum of this
        polygon with other.

        :param other: :type{Polygon} The Polygon to do a Minkowski addition with.
        :return: The convex hull around the Minkowski sum of this Polygon with other
        """

        sum = self.getMinkowskiSum(other)
        return sum.getConvexHull()

    def isInside(self, point) -> bool:
        """Whether the specified point is inside this polygon.

        If the point is exactly on the border or on a vector, it does not count
        as being inside the polygon.

        :param point: The point to check of whether it is inside.
        :return: True if it is inside, or False otherwise.
        """

        for i in range(0, len(self._points)):
            if self._isRightTurn(self._points[i], self._points[(i + 1) % len(self._points)], point) == -1: #Outside this halfplane!
                return False
        return True

    def _isRightTurn(self, p: numpy.ndarray, q: numpy.ndarray, r: numpy.ndarray) -> float:
        sum1 = q[0] * r[1] + p[0] * q[1] + r[0] * p[1]
        sum2 = q[0] * p[1] + r[0] * q[1] + p[0] * r[1]

        if sum1 - sum2 < 0:
            return 1
        elif sum1 == sum2:
            return 0
        else:
            return -1

    def _clipperPoints(self) -> numpy.ndarray:
        """
        Converts the vertices to a representation useful for PyClipper.

        This is necessary because Clipper uses integer-coordinates, but the coordinates in the rest of the front-end are
        one millimeter per unit. Without this conversion, vertices would be rounded to millimeters. With this conversion
        the units represent micrometers, allowing much greater precision.
        :return: A vertex representation useful for Clipper.
        """
        return (self.getPoints() * self.CLIPPER_PRECISION).astype(numpy.int32)



__all__ = ["Polygon"]
