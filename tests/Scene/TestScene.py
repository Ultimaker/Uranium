from unittest.mock import MagicMock

from UM.Scene.Camera import Camera
from UM.Scene.Scene import Scene
from UM.Scene.SceneNode import SceneNode


def test_ignoreSceneChanges():
    scene = Scene()
    scene.sceneChanged.emit = MagicMock()
    scene.setIgnoreSceneChanges(ignore_scene_changes = True)
    root = scene.getRoot()

    root.addChild(SceneNode())
    assert scene.sceneChanged.emit.call_count == 0

    scene.setIgnoreSceneChanges(ignore_scene_changes=False)
    root.addChild(SceneNode())
    assert scene.sceneChanged.emit.call_count == 2


def test_switchRoot():
    scene = Scene()
    new_root = SceneNode()
    scene.rootChanged = MagicMock()

    scene.setRoot(new_root)
    assert scene.getRoot() == new_root
    assert scene.rootChanged.emit.call_count == 1

    scene.setRoot(new_root)
    assert scene.rootChanged.emit.call_count == 1


def test_findObject():
    scene = Scene()
    node = SceneNode()
    scene.getRoot().addChild(node)

    assert scene.findObject(id(node)) == node
    assert scene.findObject(12) is None


def test_cameras():
    scene = Scene()
    camera_1 = Camera("camera_one")
    camera_2 = Camera("camera_two")
    scene.getRoot().addChild(camera_1)

    assert scene.findCamera("camera_one") == camera_1
    assert scene.findCamera("camera_nope") is None
    assert scene.findCamera("camera_two") is None
    scene.getRoot().addChild(camera_2)
    assert scene.findCamera("camera_two") == camera_2

    all_cameras = scene.getAllCameras()
    assert camera_1 in all_cameras
    assert camera_2 in all_cameras

    scene.setActiveCamera("camera_one")
    assert scene.getActiveCamera() == camera_1
    scene.setActiveCamera("camera_one")  # Ensure that setting it again doesn't break things.

