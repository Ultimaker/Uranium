from unittest.mock import MagicMock

from UM.Qt.QtRenderer import QtRenderer


def test_getAndSetViewportSize():
    renderer = QtRenderer()
    mocked_render_pass = MagicMock()
    renderer.addRenderPass(mocked_render_pass)
    renderer.setViewportSize(100, 200)
    mocked_render_pass.setSize.assert_called_with(100, 200)

    assert renderer.getViewportWidth() == 100
    assert renderer.getViewportHeight() == 200


def test_getAndSetWindowSize():
    renderer = QtRenderer()
    renderer.setWindowSize(300, 400)
    assert (300, 400) == renderer.getWindowSize()

