# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Math.Polygon import Polygon
from UM.Math.Float import Float

import numpy
import math
import unittest

class TestPolygon(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    ##  Tests mirroring a polygon horizontally.
    def test_mirrorHorizontal(self):
        p = Polygon(numpy.array([ #Make a triangle.
            [0.0, 0.0],
            [2.0, 0.0],
            [1.0, 2.0]
        ], numpy.float32))
        p.mirror([0, 0], [0, 1]) #Mirror over the vertical axis.
        self.assertEqual(len(p), 3)
        self.assertEqual(p[0], [0.0, 0.0])
        self.assertEqual(p[1], [-2.0, 0.0])
        self.assertEqual(p[2], [-1.0, 2.0])

    ##  Tests mirroring a polygon vertically.
    def test_mirrorVertical(self):
        p = Polygon(numpy.array([ #Make a triangle.
            [0.0, 0.0],
            [2.0, 0.0],
            [1.0, 2.0]
        ], numpy.float32))
        p.mirror([0, 0], [1, 0]) #Mirror over the horizontal axis.
        self.assertEqual(len(p), 3)
        self.assertEqual(p[0], [0.0, 0.0])
        self.assertEqual(p[1], [2.0, 0.0])
        self.assertEqual(p[2], [1.0, -2.0])

    ##  Tests mirroring a polygon horizontally on an axis that is not through
    #   the origin.
    def test_mirrorHorizontalFar(self):
        p = Polygon(numpy.array([ #Make a triangle.
            [0.0, 0.0],
            [2.0, 0.0],
            [1.0, 2.0]
        ], numpy.float32))
        p.mirror([10, 0], [0, 1]) #Mirror over the vertical axis with an offset.
        self.assertEqual(len(p), 3)
        self.assertEqual(p[0], [20.0, 0.0])
        self.assertEqual(p[1], [18.0, 0.0])
        self.assertEqual(p[2], [19.0, 2.0])

    ##  Tests mirroring a polygon diagonally.
    def test_mirrorDiagonal(self):
        p = Polygon(numpy.array([ #Make a triangle.
            [0.0, 0.0],
            [2.0, 0.0],
            [1.0, 2.0]
        ], numpy.float32))
        p.mirror([0, 4], [1, 1]) #Mirror over the diagonal axis. The diagonal axis also has an offset.
        self.assertEqual(len(p), 3)
        self.assertEqual(p[0], [-4.0, 4.0])
        self.assertEqual(p[1], [-4.0, 6.0])
        self.assertEqual(p[2], [-2.0, 5.0])

    ##  Tests mirroring a polygon with only one vertex.
    def test_mirrorSingleVertex(self):
        p = Polygon(numpy.array([[10.0, 0.0]], numpy.float32)) #Single vertex.
        p.mirror([0, 0], [1, 0]) #Mirror over the horizontal axis.
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0], [-10.0, 0.0])

    ##  Tests mirroring an empty polygon.
    def test_mirrorEmpty(self):
        p = Polygon(numpy.array([], numpy.float32)) #Empty polygon.
        p.mirror([0, 0], [1, 0]) #Mirror over the horizontal axis.
        self.assertEqual(len(p), 0)

    def test_project(self):
        p = Polygon(numpy.array([
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 2.0],
            [0.0, 2.0]
        ], numpy.float32))

        normal = numpy.array([0.0, 1.0])
        self.assertEqual((1.0, 2.0), p.project(normal))

        normal = numpy.array([1.0, 0.0])
        self.assertEqual((0.0, 1.0), p.project(normal))

        normal = numpy.array([math.sqrt(0.5), math.sqrt(0.5)])
        result = p.project(normal)
        self.assertTrue(Float.fuzzyCompare(result[0], 0.70710678), "{0} does not equal {1}".format(result[0], 0.70710678))
        self.assertTrue(Float.fuzzyCompare(result[1], 2.12132034), "{0} does not equal {1}".format(result[1], 2.12132034))

    def test_intersectsPolygon(self):
        p1 = Polygon(numpy.array([
            [ 0,  0],
            [10,  0],
            [10, 10],
            [ 0, 10]
        ], numpy.float32))

        p2 = Polygon(numpy.array([
            [ 5, 0],
            [15, 0],
            [15, 10],
            [ 5, 10]
        ], numpy.float32))
        self.verifyIntersection(p1, p2, (-5.0, 0.0))

        p2 = Polygon(numpy.array([
            [-5, 0],
            [ 5, 0],
            [ 5, 10],
            [-5, 10]
        ], numpy.float32))
        self.verifyIntersection(p1, p2, (5.0, 0.0))

        p2 = Polygon(numpy.array([
            [ 0, 5],
            [10, 5],
            [10, 15],
            [ 0, 15]
        ], numpy.float32))
        self.verifyIntersection(p1, p2, (0.0, -5.0))

        p2 = Polygon(numpy.array([
            [ 0,-5],
            [10,-5],
            [10, 5],
            [ 0, 5]
        ], numpy.float32))
        self.verifyIntersection(p1, p2, (0.0, 5.0))

        p2 = Polygon(numpy.array([
            [ 5, 5],
            [15,-5],
            [30, 5],
            [15,15]
        ], numpy.float32))
        self.verifyIntersection(p1, p2, (-5.0, 0.0))

        p2 = Polygon(numpy.array([
            [15, 0],
            [25, 0],
            [25, 10],
            [15, 10]
        ], numpy.float32))
        self.verifyIntersection(p1, p2, None)

    def verifyIntersection(self, p1, p2, required_result):
        for n in range(0, 4):
            for m in range(0, 4):
                result = p1.intersectsPolygon(p2)
                self.assertEqual(result, required_result)
                p2 = Polygon(numpy.concatenate((p2.getPoints()[1:], p2.getPoints()[0:1])))
            p1 = Polygon(numpy.concatenate((p1.getPoints()[1:], p1.getPoints()[0:1])))

if __name__ == "__main__":
    unittest.main()
