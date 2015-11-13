# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import numpy
import time

from UM.Job import Job

try:
    import scipy.spatial
    has_scipy = True
except ImportError:
    has_scipy = False

##  A class representing an arbitrary 2-dimensional polygon.
class Polygon:
    def __init__(self, points = None):
        self._points = points

    def isValid(self):
        return self._points is not None and len(self._points)

    def getPoints(self):
        return self._points

    def setPoints(self, points):
        self._points = points

    ##  Project this polygon on a line described by a normal.
    #
    #   \param normal The normal to project on.
    #   \return A tuple describing the line segment of this Polygon projected on to the infinite line described by normal.
    #           The first element is the minimum value, the second the maximum.
    def project(self, normal):
        projection_min = numpy.dot(normal, self._points[0])
        projection_max = projection_min
        for point in self._points:
            projection = numpy.dot(normal, point)
            projection_min = min(projection_min, projection)
            projection_max = max(projection_max, projection)

        return (projection_min, projection_max)

    ##  Check to see whether this polygon intersects with another polygon.
    #
    #   \param other \type{Polygon} The polygon to check for intersection.
    #   \return A tuple of the x and y distance of intersection, or None if no intersection occured.
    def intersectsPolygon(self, other):
        retSize = 10000000.0
        ret = None

        for n in range(0, len(self._points)):
            p0 = self._points[n-1]
            p1 = self._points[n]

            normal = (p1 - p0)[::-1]
            normal[1] = -normal[1]
            normal /= numpy.linalg.norm(normal)

            aMin, aMax = self.project(normal)
            bMin, bMax = other.project(normal)
            if aMin > bMax:
                return None
            if bMin > aMax:
                return None
            size = min(aMax, bMax) - max(aMin, bMin)
            if size < retSize:
                if aMin < bMin:
                    ret = normal * -size
                else:
                    ret = normal * size
                retSize = size

        for n in range(0, len(other._points)):
            p0 = other._points[n-1]
            p1 = other._points[n]

            normal = (p1 - p0)[::-1]
            normal[1] = -normal[1]
            normal /= numpy.linalg.norm(normal)

            aMin, aMax = self.project(normal)
            bMin, bMax = other.project(normal)
            if aMin > bMax:
                return None
            if bMin > aMax:
                return None
            size = min(aMax, bMax) - max(aMin, bMin)
            if size < retSize:
                if aMin < bMin:
                    ret = normal * -size
                else:
                    ret = normal * size
                retSize = size

        if ret is not None:
            return (ret[0], ret[1])
        else:
            return None

    ##  Calculate the convex hull around the set of points of this polygon.
    #
    #   \return \type{Polygon} The convex hull around the points of this polygon.
    if has_scipy:
        def getConvexHull(self):
            hull = scipy.spatial.ConvexHull(self._points)
            return Polygon(numpy.flipud(self._points[hull.vertices]))
    else:
        def getConvexHull(self):
            unique = {}
            for p in self._points:
                unique[p[0], p[1]] = 1

            points = list(unique.keys())
            points.sort()
            if len(points) < 1:
                return Polygon(numpy.zeros((0, 2), numpy.float32))
            if len(points) < 2:
                return Polygon(numpy.array(points, numpy.float32))

            # Build upper half of the hull.
            upper = [points[0], points[1]]
            for p in points[2:]:
                upper.append(p)
                while len(upper) > 2 and not self._isRightTurn(*upper[-3:]):
                    del upper[-2]

            # Build lower half of the hull.
            points = points[::-1]
            lower = [points[0], points[1]]
            for p in points[2:]:
                lower.append(p)
                while len(lower) > 2 and not self._isRightTurn(*lower[-3:]):
                    del lower[-2]

            # Remove duplicates.
            del lower[0]
            del lower[-1]

            return Polygon(numpy.array(upper + lower, numpy.float32))

    ##  Perform a Minkowski sum of this polygon with another polygon.
    #
    #   \param other The polygon to perform a Minkowski sum with.
    #   \return \type{Polygon} The Minkowski sum of this polygon with other.
    def getMinkowskiSum(self, other):
        points = numpy.zeros((len(self._points) * len(other._points), 2))
        for n in range(0, len(self._points)):
            for m in range(0, len(other._points)):
                points[n * len(other._points) + m] = self._points[n] + other._points[m]

                time.sleep(0.00001)

        return Polygon(points)

    ##  Create a Minkowski hull from this polygon and another polygon.
    #
    #   The Minkowski hull is the convex hull around the Minkowski sum of this
    #   polygon with other.
    #
    #   \param other \type{Polygon} The Polygon to do a Minkowski addition with.
    #   \return The convex hull around the Minkowski sum of this Polygon with other
    def getMinkowskiHull(self, other):
        sum = self.getMinkowskiSum(other)
        return sum.getConvexHull()

    def _isRightTurn(self, p, q, r):
        sum1 = q[0] * r[1] + p[0] * q[1] + r[0] * p[1]
        sum2 = q[0] * p[1] + r[0] * q[1] + p[0] * r[1]

        if sum1 - sum2 < 0:
            return 1
        else:
            return 0
