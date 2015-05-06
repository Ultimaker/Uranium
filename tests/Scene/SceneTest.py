# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import unittest

from UM.Scene.Scene import Scene
from UM.Scene.SceneNode import SceneNode
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
from copy import copy, deepcopy
import numpy

class SceneTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self._scene = Scene()
        self._scene_object = SceneNode()
        self._scene_object2 = SceneNode()
        self._scene_object.addChild(self._scene_object2)
        self._scene.getRoot().addChild(self._scene_object)
        temp_matrix = Matrix()
        temp_matrix.setByTranslation(Vector(10,10,10))
        self._scene_object2.setLocalTransformation(deepcopy(temp_matrix))
        temp_matrix.setByScaleFactor(0.5)
        self._scene_object.setLocalTransformation(temp_matrix)

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_checkWorldTransformation(self):
        numpy.testing.assert_array_almost_equal(self._scene_object2.getWorldTransformation().getData(), numpy.array([[0.5,0,0,5],[0,0.5,0,5],[0,0,0.5,5],[0,0,0,1]]))

if __name__ == "__main__":
    unittest.main()
