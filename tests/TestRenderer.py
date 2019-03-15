from unittest.mock import patch

from UM.View.RenderPass import RenderPass
from UM.View.Renderer import Renderer


def testAddRemoveRenderPas():
    renderer = Renderer()
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
        render_pass_1 = RenderPass("test1", 1, 1)

    renderer.addRenderPass(render_pass_1)

    assert renderer.getRenderPass("test1") == render_pass_1
    assert renderer.getRenderPass("test2") is None

    assert len(renderer.getRenderPasses()) == 1

    renderer.removeRenderPass(render_pass_1)

    assert renderer.getRenderPass("test1") is None