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
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ], numpy.float32))

        p2 = Polygon(numpy.array([
            [0.5, 0.5],
            [1.5, 0.5],
            [1.5, 1.5],
            [0.5, 1.5]
        ], numpy.float32))
        result = p1.intersectsPolygon(p2)
        print(result)

        p2 = Polygon(numpy.array([
            [2.5, 2.5],
            [3.5, 2.5],
            [3.5, 3.5],
            [2.5, 3.5]
        ], numpy.float32))
        result = p1.intersectsPolygon(p2)
        print(result)

        p1 = Polygon(numpy.array([
            [0, 0],
            [10, 0],
            [10, 10],
            [0, 10]
        ], numpy.float32))

        p2 = Polygon(numpy.array([
            [5, 5],
            [15, 5],
            [15, 15],
            [5, 15]
        ], numpy.float32))
        result = p1.intersectsPolygon(p2)
        print(result)

        p2 = Polygon(numpy.array([
            [5, 5],
            [5, 15],
            [-10, 15],
            [-10, 5]
        ], numpy.float32))
        result = p1.intersectsPolygon(p2)
        print(result)

        p2 = Polygon(numpy.array([
            [2.5, 7.5],
            [7.5, 7.5],
            [7.5, 15.0],
            [2.5, 15.0]
        ]))
        result = p1.intersectsPolygon(p2)
        print(result)

        p2 = Polygon(numpy.array([
            [2.5, 7.5],
            [-2.5, 7.5],
            [-2.5, -5.0],
            [2.5, -5.0]
        ]))
        result = p1.intersectsPolygon(p2)
        print(result)


if __name__ == "__main__":
    unittest.main()
