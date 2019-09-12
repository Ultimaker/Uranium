# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Polygon import Polygon
from UM.Math.Float import Float

import numpy
import math
import pytest

#pytestmark = pytest.mark.skip(reason = "Incomplete tests")

class TestPolygon:
    def setup_method(self, method):
        # Called before the first testfunction is executed
        pass

    def teardown_method(self, method):
        # Called after the last testfunction was executed
        pass

    def test_equalitySamePolygon(self):
        polygon = Polygon.approximatedCircle(2)
        assert polygon == polygon

    def test_equalityString(self):
        polygon = Polygon.approximatedCircle(42)
        assert polygon != "42"  # Not the answer after all!

    def test_equality(self):
        polygon_1 = Polygon.approximatedCircle(2)
        polygon_2 = Polygon.approximatedCircle(2)
        assert polygon_1 == polygon_2

    def test_inequality(self):
        # This case should short cirquit because the length of points are not the same
        polygon_1 = Polygon.approximatedCircle(2)
        polygon_2 = Polygon()
        assert polygon_1 != polygon_2

    def test_translate(self):
        polygon = Polygon(numpy.array([[0.0, 0.0], [2.0, 0.0], [1.0, 2.0]], numpy.float32))
        translated_poly = polygon.translate(2, 3)

        result = Polygon(numpy.array([[2.0, 3.0], [4.0, 3.0], [3.0, 5.0]], numpy.float32))
        assert result == translated_poly

    def test_translateInvalidPoly(self):
        polygon = Polygon()

        assert polygon == polygon.translate(2, 3)

    ##  The individual test cases for mirroring polygons.
    test_mirror_data = [
        ({ "points": [[0.0, 0.0], [2.0, 0.0], [1.0, 2.0]], "axis_point": [0, 0], "axis_direction": [0, 1], "answer": [[-1.0, 2.0], [-2.0, 0.0], [0.0, 0.0]], "label": "Mirror Horizontal", "description": "Test mirroring a polygon horizontally." }),
        ({ "points": [[0.0, 0.0], [2.0, 0.0], [1.0, 2.0]], "axis_point": [0, 0], "axis_direction": [1, 0], "answer": [[1.0, -2.0], [2.0, 0.0], [0.0, 0.0]], "label": "Mirror Vertical", "description": "Test mirroring a polygon vertically." }),
        ({ "points": [[0.0, 0.0], [2.0, 0.0], [1.0, 2.0]], "axis_point": [10, 0], "axis_direction": [0, 1], "answer": [[19.0, 2.0], [18.0, 0.0], [20.0, 0.0]], "label": "Mirror Horizontal Far", "description": "Test mirrorring a polygon horizontally on an axis that is not through the origin." }),
        ({ "points": [[0.0, 0.0], [2.0, 0.0], [1.0, 2.0]], "axis_point": [0, 4], "axis_direction": [1, 1], "answer": [[-2.0, 5.0], [-4.0, 6.0], [-4.0, 4.0]], "label": "Mirror Diagonal", "description": "Test mirroring a polygon diagonally." }),
        ({ "points": [], "axis_point": [0, 0], "axis_direction": [1, 0], "answer": [], "label": "Mirror Empty", "description": "Test mirroring an empty polygon." }),
        ({ "points": [[0.0, 0.0], [2.0, 0.0], [1.0, 2.0]], "axis_point": [0, 4], "axis_direction": [0, 0], "answer": [[0.0, 0.0], [2.0, 0.0], [1.0, 2.0]], "label": "Mirror Diagonal", "description": "Test mirroring with wrong axis"}),
    ]

    ##  Tests the mirror function.
    #
    #   \param data The data of the test. Must include a list of points of the
    #   polygon to mirror, a point on the axis, a direction of the axis and an
    #   answer that is the result of the mirroring.
    @pytest.mark.parametrize("data", test_mirror_data)
    def test_mirror(self, data):
        polygon = Polygon(numpy.array(data["points"], numpy.float32)) #Create a polygon with the specified points.
        mirrored_poly = polygon.mirror(data["axis_point"], data["axis_direction"]) #Mirror over the specified axis.
        points = mirrored_poly.getPoints()
        assert len(points) == len(data["points"]) #Must have the same amount of vertices.
        for point_index in range(len(points)):
            assert len(points[point_index]) == len(data["answer"][point_index]) #Same dimensionality (2).
            for dimension in range(len(points[point_index])):
                assert Float.fuzzyCompare(points[point_index][dimension], data["answer"][point_index][dimension]) #All points must be equal.

    ##  The individual test cases for the projection tests.
    test_project_data = [
        ({ "normal": [0.0, 1.0], "answer": [1.0, 2.0], "label": "Project Vertical", "description": "Project the polygon onto a vertical line." }),
        ({ "normal": [1.0, 0.0], "answer": [0.0, 1.0], "label": "Project Horizontal", "description": "Project the polygon onto a horizontal line." }),
        ({ "normal": [math.sqrt(0.5), math.sqrt(0.5)], "answer": [math.sqrt(0.5), math.sqrt(4.5)], "label": "Project Diagonal", "description": "Project the polygon onto a diagonal line." })
    ]

    ##  Tests the project function.
    #
    #   \param data The data of the test. Must include a normal vector to
    #   project on and a pair of coordinates that is the answer.
    @pytest.mark.parametrize("data", test_project_data)
    def test_project(self, data):
        p = Polygon(numpy.array([
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 2.0],
            [0.0, 2.0]
        ], numpy.float32))
        result = p.project(data["normal"])  # Project the polygon onto the specified normal vector.
        assert len(result) == len(data["answer"])  # Same dimensionality (2).
        for dimension in range(len(result)):
            assert Float.fuzzyCompare(result[dimension], data["answer"][dimension])

    ##  The individual test cases for the intersection tests.
    test_intersect_data = [
        ({ "polygon": [[ 5.0,  0.0], [15.0,  0.0], [15.0, 10.0], [ 5.0, 10.0]], "answer": [ 5.0,  10], "label": "Intersect Simple", "description": "Intersect with a polygon that fully intersects." }),
        ({ "polygon": [[-5.0,  0.0], [ 5.0,  0.0], [ 5.0, 10.0], [-5.0, 10.0]], "answer": [ 5.0,  10.0], "label": "Intersect Left", "description": "Intersect with a polygon on the negative x-axis side that fully intersects." }),
        ({ "polygon": [[ 0.0,  5.0], [10.0,  5.0], [10.0, 15.0], [ 0.0, 15.0]], "answer": [ 10.0, 5.0], "label": "Intersect Straight Above", "description": "Intersect with a polygon that is exactly above the base polygon (edge case)." }),
        ({ "polygon": [[ 0.0, -5.0], [10.0, -5.0], [10.0,  5.0], [ 0.0,  5.0]], "answer": [ 10.0,  5.0], "label": "Intersect Straight Left", "description": "Intersect with a polygon that is exactly left of the base polygon (edge case)." }),
        ({ "polygon": [[15.0,  0.0], [25.0,  0.0], [25.0, 10.0], [15.0, 10.0]], "answer": None,         "label": "Intersect Miss", "description": "Intersect with a polygon that doesn't intersect at all." }),
        ({"polygon": [[15.0, 0.0]], "answer": None, "label": "Intersect invalid", "description": "Intersect with a polygon that is a single point"})

    ]

    ##  Tests the polygon intersect function.
    #
    #   Every test case intersects a parametrised polygon with a base square of
    #   10 by 10 units at the origin.
    #
    #   \param data The data of the test. Must include a polygon to intersect
    #   with and a required answer.
    @pytest.mark.parametrize("data", test_intersect_data)
    def test_intersectsPolygon(self, data):
        p1 = Polygon(numpy.array([  # The base polygon to intersect with.
            [ 0,  0],
            [10,  0],
            [10, 10],
            [ 0, 10]
        ], numpy.float32))
        p2 = Polygon(numpy.array(data["polygon"]))  # The parametrised polygon to intersect with.

        # Shift the order of vertices in both polygons around. The outcome should be independent of what the first vertex is.
        for n in range(0, len(p1.getPoints())):
            for m in range(0, len(data["polygon"])):
                result = p1.intersectsPolygon(p2)
                if not data["answer"]:  # Result should be None.
                    assert result is None
                else:
                    assert result is not None
                    for i in range(0, len(data["answer"])):
                        assert Float.fuzzyCompare(result[i], data["answer"][i])
                p2 = Polygon(numpy.roll(p2.getPoints(), 1, axis = 0)) #Shift p2.
            p1 = Polygon(numpy.roll(p1.getPoints(), 1, axis = 0)) #Shift p1.

    ##  The individual test cases for convex hull intersection tests.
    test_intersectConvex_data = [
        ({ "p1": [[-42, -32], [-42, 12], [62, 12], [62, -32]], "p2": [[-62, -12], [-62, 32], [42, 32], [42, -12]], "answer": [[-42, -12], [-42, 12], [42, 12], [42, -12]], "label": "UM2 Fans", "description": "A simple intersection without edge cases of UM2 fans collision area." })
    ]

    ##  Tests the convex hull intersect function.
    #
    #   \param data The data of the test case. Must include two polygons and a
    #   required result polygon.
    @pytest.mark.parametrize("data", test_intersectConvex_data)
    def test_intersectConvexHull(self, data) -> None:
        p1 = Polygon(numpy.array(data["p1"]))
        p2 = Polygon(numpy.array(data["p2"]))
        result = p1.intersectionConvexHulls(p2)
        assert len(result.getPoints()) == len(data["answer"])  # Same amount of vertices.
        isCorrect = False
        for rotation in range(0, len(result.getPoints())):  # The order of vertices doesn't matter, so rotate the result around and if any check succeeds, the answer is correct.
            thisCorrect = True  # Is this rotation correct?
            for vertex in range(0, len(result.getPoints())):
                for dimension in range(0, len(result.getPoints()[vertex])):
                    if not Float.fuzzyCompare(result.getPoints()[vertex][dimension], data["answer"][vertex][dimension]):
                        thisCorrect = False
                        break  # Break out of two loops.
                if not thisCorrect:
                    break
            if thisCorrect:  # All vertices checked and it's still correct.
                isCorrect = True
                break
            result = Polygon(numpy.roll(result.getPoints(), 1, axis = 0)) #Perform the rotation for the next check.
        assert isCorrect

    ##  The individual test cases for convex hull union tests.
    test_unionConvex_data = [
        ({"p1": [[1, 1], [1.5, 1], [2, 2], [2, 0]], "p2": [[3, 2], [3.5, 1], [4, 1], [3, 0]], "answer": [[1, 1], [2, 2], [3, 2], [4, 1], [3, 0], [2, 0]], "label": "ConvexHull Union Separate", "description": "Two disparate shapes."}),
        ({"p1": [[1, 1], [3, 3], [3, -1]], "p2": [[2, 1], [4, 2], [4, 0]], "answer": [[1, 1], [3, 3], [4, 2], [4, 0], [3, -1]], "label": "ConvexHull Union Inside", "description": "One triangle partially inside the other."}),
        ({"p1": [[1, 1], [5, 5], [5, -4]], "p2": [[2, 1], [3, 2], [3, 1]], "answer": [[1, 1], [5, 5], [5, -4]], "label": "ConvexHull Union Enclosed", "description": "One triangle completely inside the other."}),
        ({"p1": [[1, 1], [2, 2], [2, 0]], "p2": [], "answer": [[1, 1], [2, 2], [2, 0]], "label": "ConvexHull Union Single", "description": "One triangle."})
    ]

    ##  Tests the convex hull of convex hulls
    #
    #   \param data The data of the test case.
    @pytest.mark.parametrize("data", test_unionConvex_data)
    def test_unionConvexHull(self, data) -> None:
        p1 = Polygon(numpy.array(data["p1"]))
        p2 = Polygon(numpy.array(data["p2"]))
        result = p1.unionConvexHulls(p2)
        assert len(result.getPoints()) == len(data["answer"])  # Same amount of vertices.
        isCorrect = False
        for rotation in range(0, len(result.getPoints())):  # The order of vertices doesn't matter, so rotate the result around and if any check succeeds, the answer is correct.
            thisCorrect = True  # Is this rotation correct?
            for vertex in range(0, len(result.getPoints())):
                for dimension in range(0, len(result.getPoints()[vertex])):
                    if not Float.fuzzyCompare(result.getPoints()[vertex][dimension], data["answer"][vertex][dimension]):
                        thisCorrect = False
                        break  # Break out of two loops.
                if not thisCorrect:
                    break
            if thisCorrect:  # All vertices checked and it's still correct.
                isCorrect = True
                break
            result = Polygon(numpy.roll(result.getPoints(), 1, axis = 0)) #Perform the rotation for the next check.
        assert isCorrect

    def test_isInside(self):
        polygon = Polygon.approximatedCircle(5)
        assert polygon.isInside((0, 0))

        assert not polygon.isInside((9001, 9001))
