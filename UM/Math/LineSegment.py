# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional

from UM.Math.Float import Float  # For fuzzy comparison of edge cases.
from UM.Math.Vector2 import Vector2 #Just for type checking.

##  Represents a line segment in 2D.
#
#   The line segment is represented by two endpoints.
class LineSegment:
    ##  Creates a new line segment with the specified endpoints.
    #
    #   \param endpoint_a An endpoint of the line segment.
    #   \param endpoint_b An endpoint of the line segment.
    def __init__(self, endpoint_a: Vector2, endpoint_b: Vector2) -> None:
        self._endpoint_a = endpoint_a # type: Vector2
        self._endpoint_b = endpoint_b # type: Vector2

    ##  Gets the second endpoint (B) of the line segment.
    #
    #   \return The second endpoint of the line segment.
    def getEnd(self) -> Vector2:
        return self._endpoint_b

    ##  Gets the first endpoint (A) of the line segment.
    #
    #   \return The first endpoint of the line segment.
    def getStart(self) -> Vector2:
        return self._endpoint_a

    ##  Returns the point of intersection of this line segment with another line
    #   segment, if any.
    #
    #   \param other The line segment to check intersection with.
    #   \return The intersection point if they intersect, or None otherwise.
    def intersection(self, other: "LineSegment") -> Optional[Vector2]:
        if not self.intersectsWithLine(other._endpoint_a, other._endpoint_b) or not other.intersectsWithLine(self._endpoint_a, self._endpoint_b): #Line segments don't intersect.
            return None
        direction_me = self._endpoint_b - self._endpoint_a
        direction_other = other._endpoint_b - other._endpoint_a
        diff_endpoint_a = self._endpoint_a - other._endpoint_a
        perpendicular = direction_me.perpendicular()
        denominator = perpendicular.dot(direction_other) #Project onto the perpendicular.
        numerator = perpendicular.dot(diff_endpoint_a)
        if denominator == 0: #Lines are parallel.
            return None
        return (numerator / denominator.astype(float)) * direction_other + other._endpoint_a

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
    def intersectsWithLine(self, a: Vector2, b: Vector2) -> bool:
        shifted_b = b - a
        #It intersects if either endpoint is on the line, or if one endpoint is on the right but the other is not.
        return Float.fuzzyCompare(shifted_b.cross(self._endpoint_a), 0) or Float.fuzzyCompare(shifted_b.cross(self._endpoint_b), 0) or (self._pointIsRight(self._endpoint_a, a, b) != self._pointIsRight(self._endpoint_b, a, b))

    ##  Determines whether point p is to the right of the line through a and b.
    #
    #   \param p The point to determine whether it is to the right of the line.
    #   \param a A point on the line.
    #   \param b Another point on the line.
    def _pointIsRight(self, p: Vector2, a: Vector2, b: Vector2) -> bool:
        shifted_end = b - a
        return shifted_end.cross(p - a) < 0