# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import numpy

from UM.Math.Float import Float #For fuzzy comparison of edge cases.
from UM.Math.LineSegment import LineSegment #For line-line intersections for computing polygon intersections.
from UM.Math.Vector2 import Vector2 #For constructing line segments for polygon intersections.
from UM.Logger import Logger

from UM.Math import NumPyUtil

try:
    import scipy.spatial
    has_scipy = True
except ImportError:
    has_scipy = False


##  A class representing an immutable arbitrary 2-dimensional polygon.
class Polygon:
    ##  Return vertices from an approximate circle.
    #
    #   An octagon is returned, which comes close enough to a circle.
    #
    #   \param radius The radius of the circle.
    #   \return A polygon that approximates a circle.
    @staticmethod
    def approximatedCircle(radius):
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

    def __init__(self, points = None):
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

    ##  Gives a debugging representation of the polygon.
    #
    #   This lists the polygon's coordinates, like so::
    #     [[0,0], [1,3], [3,0]]
    #
    #   \return A representation of the polygon that is useful for debugging.
    def __repr__(self):
        coordinates = (("[" + str(point[0]) + "," + str(point[1]) + "]") for point in self._points)
        return "[" + ", ".join(coordinates) + "]"

    def isValid(self):
        return self._points is not None and len(self._points)

    def getPoints(self):
        return self._points

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

    ##  Moves the polygon by a fixed offset.
    #
    #   \param x The distance to move along the X-axis.
    #   \param y The distance to move along the Y-axis.
    def translate(self, x = 0, y = 0):
        if self.isValid():
            return Polygon(numpy.add(self._points, numpy.array([[x, y]])))
        else:
            return self

    ##  Mirrors this polygon across the specified axis.
    #
    #   \param point_on_axis A point on the axis to mirror across.
    #   \param axis_direction The direction vector of the axis to mirror across.
    def mirror(self, point_on_axis, axis_direction):
        #Input checking.
        if axis_direction == [0, 0, 0]:
            Logger.log("w", "Tried to mirror a polygon over an axis with direction [0, 0, 0].")
            return #Axis has no direction. Can't expect us to mirror anything!
        axis_direction /= numpy.linalg.norm(axis_direction) #Normalise the direction.
        if not self.isValid(): # Not a valid polygon, so don't do anything.
            return self

        #In order to be able to mirror points around an arbitrary axis, we have to normalize the axis and all points such that the axis goes through the origin.
        point_matrix = numpy.matrix(self._points)
        point_matrix -= point_on_axis #Moves all points such that the axis origin is at [0,0].

        #To mirror a coordinate, we have to add the projection of the point to the axis twice (where v is the vector to reflect):
        #  reflection(v) = 2 * projection(v) - v
        #Writing out the projection, this becomes (where l is the normalised direction of the line):
        #  reflection(v) = 2 * (l . v) l - v
        #With Snell's law this can be simplified to the Householder transformation matrix:
        #  reflection(v) = R v
        #  R = 2 l l^T - I
        #This simplifies the entire reflection to one big matrix transformation.
        axis_matrix = numpy.matrix(axis_direction)
        reflection = 2 * numpy.transpose(axis_matrix) * axis_matrix - numpy.identity(2)
        point_matrix = point_matrix * reflection #Apply the actual transformation.

        #Shift the points back to the original coordinate space before the axis was normalised to the origin.
        point_matrix += point_on_axis
        return Polygon(point_matrix.getA()[::-1])

    ##  Computes the intersection of the convex hulls of this and another
    #   polygon.
    #
    #   This is an implementation of O'Rourke's "Chase" algorithm. For a more
    #   detailed description of why the algorithm works the way it does, please
    #   consult the book "Computational Geometry in C", second edition, chapter
    #   7.6.
    #
    #   \param other The other polygon to intersect convex hulls with.
    #   \return The intersection of the two polygons' convex hulls.
    def intersectionConvexHulls(self, other):
        me = self.getConvexHull()
        him = other.getConvexHull()

        if len(me._points) <= 2 or len(him._points) <= 2: #If either polygon has no surface area, then the intersection is empty.
            return Polygon()

        index_me = 0 #The current vertex index.
        index_him = 0
        advances_me = 0 #How often we've advanced.
        advances_him = 0
        who_is_inside = "unknown" #Which of the two polygons is currently on the inside.
        directions_me = numpy.subtract(numpy.roll(me._points, -1, axis = 0), me._points) #Pre-compute the difference between consecutive points to get a direction for each point.
        directions_him = numpy.subtract(numpy.roll(him._points, -1, axis = 0), him._points)
        result = []

        #Iterate through both polygons to find intersections and inside vertices until we've made a loop through both polygons.
        while advances_me <= len(me._points) or advances_him <= len(him._points):
            vertex_me = me._points[index_me]
            vertex_him = him._points[index_him]
            if advances_me > len(me._points) * 2 or advances_him > len(him._points) * 2: #Also, if we've looped twice through either polygon, the boundaries of the polygons don't intersect.
                if len(result) > 2:
                    return Polygon(points = result)
                if me.isInside(vertex_him): #Other polygon is inside this one.
                    return him
                if him.isInside(vertex_me): #This polygon is inside the other.
                    return me
                #Polygons are disjunct.
                return Polygon()

            me_start = Vector2(data = vertex_me)
            me_end = Vector2(data = vertex_me + directions_me[index_me])
            him_start = Vector2(data = vertex_him)
            him_end = Vector2(data = vertex_him + directions_him[index_him])

            me_in_him_halfplane = (me_end - him_start).cross(him_end - him_start) #Cross gives positive if him_end is to the left of me_end (as seen from him_start).
            him_in_me_halfplane = (him_end - me_start).cross(me_end - me_start) #Arr, I's got him in me halfplane, cap'n.
            intersection = LineSegment(me_start, me_end).intersection(LineSegment(him_start, him_end))

            if intersection:
                result.append(intersection.getData()) #The intersection is always in the hull.
                if me_in_him_halfplane > 0: #At the intersection, who was inside changes.
                    who_is_inside = "me"
                elif him_in_me_halfplane > 0:
                    who_is_inside = "him"
                else:
                    pass #Otherwise, whoever is inside remains the same (or unknown).
                advances_me += 1
                index_me = advances_me % len(me._points)
                advances_him += 1
                index_him = advances_him % len(him._points)
                continue

            cross = (Vector2(data = directions_me[index_me]).cross(Vector2(data = directions_him[index_him])))

            #Edge case: Two exactly opposite edges facing away from each other.
            if Float.fuzzyCompare(cross, 0) and me_in_him_halfplane <= 0 and him_in_me_halfplane <= 0:
                # The polygons must be disjunct then.
                return Polygon()

            #Edge case: Two colinear edges.
            if Float.fuzzyCompare(cross, 0) and me_in_him_halfplane <= 0:
                advances_me += 1
                index_me = advances_me % len(me._points)
                continue
            if Float.fuzzyCompare(cross, 0) and him_in_me_halfplane <= 0:
                advances_him += 1
                index_him = advances_him % len(him._points)
                continue

            #Edge case: Two edges overlap.
            if Float.fuzzyCompare(cross, 0):
                #Just advance the outside.
                if who_is_inside == "me":
                    advances_him += 1
                    index_him = advances_him % len(him._points)
                else: #him or unknown. If it's unknown, it doesn't matter which one is advanced, as long as it's the same polygon being advanced every time (me in this case).
                    advances_me += 1
                    index_me = advances_me % len(me._points)
                continue

            #Generic case: Advance whichever polygon is on the outside.
            if cross >= 0: #This polygon is going faster towards the inside.
                if him_in_me_halfplane > 0:
                    advances_me += 1
                    index_me = advances_me % len(me._points)
                    if who_is_inside == "him":
                        result.append(vertex_him)
                else:
                    advances_him += 1
                    index_him = advances_him % len(him._points)
                    if who_is_inside == "me":
                        result.append(vertex_me)
            else: #The other polygon is going faster towards the inside.
                if me_in_him_halfplane > 0:
                    advances_him += 1
                    index_him = advances_him % len(him._points)
                    if who_is_inside == "me":
                        result.append(vertex_me)
                else:
                    advances_me += 1
                    index_me = advances_me % len(me._points)
                    if who_is_inside == "him":
                        result.append(vertex_him)
        if (result[0] == result[-1]).all(): #If the last two edges are parallel, the first vertex will have been added again. So if it is the same as the last element, remove it.
            result = result[:-1] #This also handles the case where the intersection is only one point.
        return Polygon(points = result)

    ##  Check to see whether this polygon intersects with another polygon.
    #
    #   \param other \type{Polygon} The polygon to check for intersection.
    #   \return A tuple of the x and y distance of intersection, or None if no intersection occured.
    def intersectsPolygon(self, other):
        if len(self._points) < 2 or len(other.getPoints()) < 2:  # Polygon has not enough points, so it cant intersect.
            return None

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
            points = self._points

            if len(points) < 1:
                return Polygon(numpy.zeros((0, 2), numpy.float64))
            if len(points) <= 2:
                return Polygon(numpy.array(points, numpy.float64))

            try:
                hull = scipy.spatial.ConvexHull(points)
            except scipy.spatial.qhull.QhullError:
                return Polygon(numpy.zeros((0, 2), numpy.float64))

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
                while len(upper) > 2 and self._isRightTurn(*upper[-3:]) != 1:
                    del upper[-2]

            # Build lower half of the hull.
            points = points[::-1]
            lower = [points[0], points[1]]
            for p in points[2:]:
                lower.append(p)
                while len(lower) > 2 and self._isRightTurn(*lower[-3:]) != 1:
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

    ##  Whether the specified point is inside this polygon.
    #
    #   If the point is exactly on the border or on a vector, it does not count
    #   as being inside the polygon.
    #
    #   \param point The point to check of whether it is inside.
    #   \return True if it is inside, or False otherwise.
    def isInside(self, point):
        for i in range(0,len(self._points)):
            if self._isRightTurn(self._points[i], self._points[(i + 1) % len(self._points)], point) == -1: #Outside this halfplane!
                return False
        return True

    def _isRightTurn(self, p, q, r):
        sum1 = q[0] * r[1] + p[0] * q[1] + r[0] * p[1]
        sum2 = q[0] * p[1] + r[0] * q[1] + p[0] * r[1]

        if sum1 - sum2 < 0:
            return 1
        elif sum1 == sum2:
            return 0
        else:
            return -1
