
import pytest
from unittest.mock import patch, mock_open, MagicMock

from UM.View.GL.OpenGLContext import OpenGLContext

context_without_extensions = MagicMock()
context_without_extensions.hasExtension = MagicMock(return_value = False)

context_with_extensions = MagicMock()
context_with_extensions.hasExtension = MagicMock(return_value = True)


def test_setContext():
    surface_format = MagicMock()
    opengl_context = MagicMock()
    opengl_context.create = MagicMock(return_value = True)
    with patch("UM.View.GL.OpenGLContext.QSurfaceFormat", MagicMock(return_value = surface_format)):
        with patch("UM.View.GL.OpenGLContext.QOpenGLContext", MagicMock(return_value=opengl_context)):
            assert OpenGLContext.setContext(1,2) == opengl_context
            opengl_context.setFormat.assert_called_once_with(surface_format)


def test_setContext_failed():
    surface_format = MagicMock()
    opengl_context = MagicMock()
    opengl_context.create = MagicMock(return_value=False)
    with patch("UM.View.GL.OpenGLContext.QSurfaceFormat", MagicMock(return_value=surface_format)):
        with patch("UM.View.GL.OpenGLContext.QOpenGLContext", MagicMock(return_value=opengl_context)):
            assert OpenGLContext.setContext(1, 2) is None


@pytest.mark.parametrize("context, major_version, minor_version, result", [(context_with_extensions, 4, 1, True),
                                                                           (context_with_extensions, 5, 0, True),
                                                                           (context_with_extensions, 3, 0, True),
                                                                           (context_without_extensions, 3, 0, False),
                                                                           (context_without_extensions, 4, 1, True)])
def test_supportsVertexArrayObjects(context, major_version, minor_version, result):
    OpenGLContext.major_version = major_version
    OpenGLContext.minor_version = major_version
    assert OpenGLContext.supportsVertexArrayObjects(context) == result


@pytest.mark.parametrize("major_version, minor_version, result", [(3, 9009, True),
                                                                  (4, 0, True),
                                                                  (4, 1, False),
                                                                  (5, 2, False)])
def test_isLegacyOpenGl(major_version, minor_version, result):
    OpenGLContext.major_version = major_version
    OpenGLContext.minor_version = minor_version
    assert OpenGLContext.isLegacyOpenGL() == result
