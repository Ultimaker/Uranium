# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from Float import Float

##  Represents a line segment in 2D.
#
#   The line segment is represented by a beginning and an end point.
class LineSegment(object):
    ##  Creates a new line segment with the specified start and end points.
    #
    #   \param start The start point of the line segment.
    #   \param end The end point of the line segment.
    def __init__(self, start, end):
        self._start = start
        self._end = end

    ##  Gets the ending point of the line segment.
    #
    #   \return The ending point of the line segment.
    def getEnd(self):
        return self._end

    ##  Gets the starting point of the line segment.
    #
    #   \return The starting point of the line segment.
    def getStart(self):
        return self._start

    ##  Returns the point of intersection of this line segment with another line
    #   segment, if any.
    #
    #   \param other The line segment to check intersection with.
    #   \return The intersection point if they intersect, or None otherwise.
    def intersection(self, other):
        if not self.intersectsWithLine(other._start, other._end) or not other.intersectsWithLine(self._start, self._end): #Line segments don't intersect.
            return None
        direction_me = self._end - self._start
        direction_other = other._end - other._start
        diff_starts = self._start - other._start
        perpendicular = direction_me.perpendicular()
        denominator = perpendicular.dot(direction_other) #Project onto the perpendicular.
        numerator = perpendicular.dot(diff_starts)
        print(numerator, "/", denominator)
        if denominator == 0: #Lines are parallel.
            return None
        return (numerator / denominator.astype(float)) * direction_other + other._start

    ##  Returns whether the line segment intersects the specified (infinite)
    #   line.
    #
    #   If the line segment touches the line with one or both endpoints, that
    #   counts as an intersection too.
    #
    #   \param a A point on the line to intersect with.
    #   \param b A different point on the line to intersect with.
    #   \return True if the line segment intersects with the line, or False
    #   otherwise.
    def intersectsWithLine(self, a, b):
        shifted_b = b - a
        #It intersects if either endpoint is on the line, or if one endpoint is on the right but the other is not.
        return Float.fuzzyCompare(shifted_b.cross(self._start), 0) or Float.fuzzyCompare(shifted_b.cross(self._end), 0) or (self._pointIsRight(self._start, a, b) != self._pointIsRight(self._end, a, b))

    ##  Determines whether point p is to the right of the line through start and
    #   end.
    #
    #   \param p The point to determine whether it is to the right of the line.
    #   \param start A point on the line.
    #   \param end Another point on the line.
    def _pointIsRight(self, p, start, end):
        shifted_end = end - start
        return shifted_end.cross(p) < 0