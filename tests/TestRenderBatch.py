from unittest.mock import MagicMock, patch

import pytest

from UM.Math.Color import Color
from UM.Math.Matrix import Matrix
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData
from UM.View.RenderBatch import RenderBatch


test_addItem_data = [
    {"item": {"transformation": Matrix(), "mesh": MeshData()}, "should_add": True},
    {"item": {"transformation": None, "mesh": MeshData()}, "should_add": False},
    {"item": {"transformation": None, "mesh": None}, "should_add": False},
    {"item": {"transformation": Matrix(), "mesh": None}, "should_add": False},
    {"item": {"transformation": Matrix(), "mesh": MeshData(), "uniforms": {}}, "should_add": True},
]


test_compare_data = [
    {"item1": {}, "item2": {"sort": 1}},
    {"item1": {}, "item2": {"sort": 1}},
    {"item1": {"type": RenderBatch.RenderType.Solid, "sort": 0}, "item2": {"sort": 20, "type":RenderBatch.RenderType.NoType}},  # Solid trumps notype, even if sort is higher
    {"item1": {"type": RenderBatch.RenderType.Transparent, "sort": 0}, "item2": {"sort": 20, "type":RenderBatch.RenderType.NoType}}
]


def test_createRenderBatch():
    mocked_shader = MagicMock()
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
        render_batch = RenderBatch(mocked_shader)


    #  Ensure that the proper defaults are set.
    assert render_batch.renderType == RenderBatch.RenderType.Solid
    assert render_batch.renderMode == RenderBatch.RenderMode.Triangles
    assert render_batch.shader == mocked_shader
    assert not render_batch.backfaceCull
    assert render_batch.renderRange is None
    assert render_batch.items == []


@pytest.mark.parametrize("data", test_addItem_data)
def test_addItem(data):
    mocked_shader = MagicMock()
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
        render_batch = RenderBatch(mocked_shader)

    render_batch.addItem(**data["item"])

    if data["should_add"]:
        assert len(render_batch.items) != 0


@pytest.mark.parametrize("data", test_compare_data)
def test_compare(data):
    mocked_shader = MagicMock()
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
        render_batch_1 = RenderBatch(mocked_shader, **data["item1"])
        render_batch_2 = RenderBatch(mocked_shader, **data["item2"])
    assert render_batch_1 < render_batch_2


def test_render():
    mocked_shader = MagicMock()
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
        render_batch = RenderBatch(mocked_shader)

    # Render without a camera shouldn't cause any effect.
    render_batch.render(None)
    assert mocked_shader.bind.call_count == 0

    # Rendering with a camera should cause the shader to be bound and released (even if the batch is empty)
    mocked_camera = MagicMock()
    mocked_camera.getWorldTransformation = MagicMock(return_value = Matrix())
    mocked_camera.getViewProjectionMatrix = MagicMock(return_value=Matrix())
    with patch("UM.View.GL.OpenGLContext.OpenGLContext.properties"):
        render_batch.render(mocked_camera)
    assert mocked_shader.bind.call_count == 1
    assert mocked_shader.release.call_count == 1

    # Actualy render with an item in the batch
    mb = MeshBuilder()
    mb.addPyramid(10, 10, 10, color=Color(0.0, 1.0, 0.0, 1.0))
    mb.calculateNormals()
    mesh_data = mb.build()
    render_batch.addItem(Matrix(), mesh_data, {})
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
        with patch("UM.View.GL.OpenGLContext.OpenGLContext.properties"):
            render_batch.render(mocked_camera)
    assert mocked_shader.bind.call_count == 2
    assert mocked_shader.release.call_count == 2