# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional, Tuple, List, Union

import numpy
import scipy.spatial

from UM.Logger import Logger
from UM.Math import NumPyUtil
from UM.Math import ShapelyUtil

class Polygon:
    """A class representing an immutable arbitrary 2-dimensional polygon."""

    @staticmethod
    def approximatedCircle(radius):
        """Return vertices from an approximate circle.

        An octagon is returned, which comes close enough to a circle.

        :param radius: The radius of the circle.
        :return: A polygon that approximates a circle.
        """

        return Polygon(points = numpy.array([
            [-radius, 0],
            [-radius * 0.707, radius * 0.707],
            [0, radius],
            [radius * 0.707, radius * 0.707],
            [radius, 0],
            [radius * 0.707, -radius * 0.707],
            [0, -radius],
            [-radius * 0.707, -radius * 0.707]
        ], numpy.float32))

    def __init__(self, points: Optional[Union[numpy.ndarray, List]] = None):
        self._points = NumPyUtil.immutableNDArray(points)

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

    def getPoints(self) -> numpy.array:
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
        point_matrix = numpy.matrix(self._points)
        point_matrix -= point_on_axis  # Moves all points such that the axis origin is at [0,0].

        # To mirror a coordinate, we have to add the projection of the point to the axis twice
        # (where v is the vector to reflect):
        #  reflection(v) = 2 * projection(v) - v
        # Writing out the projection, this becomes (where l is the normalised direction of the line):
        #  reflection(v) = 2 * (l . v) l - v
        # With Snell's law this can be simplified to the Householder transformation matrix:
        #  reflection(v) = R v
        #  R = 2 l l^T - I
        # This simplifies the entire reflection to one big matrix transformation.
        axis_matrix = numpy.matrix(axis_direction)
        reflection = 2 * numpy.transpose(axis_matrix) * axis_matrix - numpy.identity(2)
        point_matrix = point_matrix * reflection  # Apply the actual transformation.

        # Shift the points back to the original coordinate space before the axis was normalised to the origin.
        point_matrix += point_on_axis
        return Polygon(point_matrix.getA()[::-1])

    def intersectionConvexHulls(self, other: "Polygon") -> "Polygon":
        """Computes the intersection of the convex hulls of this and another
        polygon.

        :param other: The other polygon to intersect convex hulls with.
        :return: The intersection of the two polygons' convex hulls.
        """

        me = self.getConvexHull()
        him = other.getConvexHull()

        # If either polygon has no surface area, then the intersection is empty.
        if len(me._points) <= 2 or len(him._points) <= 2:
            return Polygon()

        polygen_me = ShapelyUtil.polygon2ShapelyPolygon(me)
        polygon_him = ShapelyUtil.polygon2ShapelyPolygon(him)

        polygon_intersection = polygen_me.intersection(polygon_him)
        if polygon_intersection.area == 0:
            return Polygon()

        points = [list(p) for p in polygon_intersection.exterior.coords]
        if points[0] == points[-1]:
            points.pop()
        return Polygon(points)

    #  Computes the convex hull of the union of the convex hulls of this and another polygon.
    #
    #   \param other The other polygon to combine convex hulls with.
    #   \return The convex hull of the union of the two polygons' convex hulls.
    def unionConvexHulls(self, other: "Polygon") -> "Polygon":
        my_hull = self.getConvexHull()
        other_hull = other.getConvexHull()

        if not my_hull.isValid():
            return other_hull
        if not other_hull.isValid():
            return my_hull

        my_polygon = ShapelyUtil.polygon2ShapelyPolygon(my_hull)
        other_polygon = ShapelyUtil.polygon2ShapelyPolygon(other_hull)

        polygon_union = my_polygon.union(other_polygon).convex_hull
        if polygon_union.area == 0:
            return Polygon()

        return Polygon(points = [list(p) for p in polygon_union.exterior.coords[:-1]])

    def intersectsPolygon(self, other: "Polygon") -> Optional[Tuple[float, float]]:
        """Check to see whether this polygon intersects with another polygon.

        :param other: :type{Polygon} The polygon to check for intersection.
        :return: A tuple of the x and y distance of intersection, or None if no intersection occured.
        """

        if not self.isValid() or not other.isValid():
            return None

        polygon_me = ShapelyUtil.polygon2ShapelyPolygon(self)
        polygon_other = ShapelyUtil.polygon2ShapelyPolygon(other)
        if polygon_other.is_empty or polygon_me.is_empty:
            return None
        if not (polygon_me.is_valid and polygon_other.is_valid):  # If not valid
            return None

        polygon_intersection = polygon_me.intersection(polygon_other)
        ret_size = None
        if polygon_intersection and polygon_intersection.area > 0:
            ret_size = (polygon_intersection.bounds[2] - polygon_intersection.bounds[0],
                        polygon_intersection.bounds[3] - polygon_intersection.bounds[1],
                        )
        return ret_size

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


__all__ = ["Polygon"]
