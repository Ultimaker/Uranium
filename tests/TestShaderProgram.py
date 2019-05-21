from unittest.mock import MagicMock, call

import pytest
from PyQt5.QtGui import QOpenGLShader

from UM.View.GL.ShaderProgram import ShaderProgram, InvalidShaderProgramError
import os

def test_ShaderProgramInit():
    # Creating it just shouldn't fail.
    shader = ShaderProgram()


def test_loadEmpty():
    shader = ShaderProgram()
    with pytest.raises(InvalidShaderProgramError):
        shader.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Shaders", "empty.shader"))


def test_loadInvalid():
    shader = ShaderProgram()
    with pytest.raises(InvalidShaderProgramError):
        shader.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Shaders", "invalid.shader"))

    with pytest.raises(InvalidShaderProgramError):
        shader.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Shaders", "invalid2.shader"))

def test_load():
    shader = ShaderProgram()

    mocked_shader_program = MagicMock()

    shader._shader_program = mocked_shader_program
    shader.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Shaders", "test.shader"))

    # It should be called 3 times, once for vertex, once for fragment and once for geometry
    call_arg_list = mocked_shader_program.addShaderFromSourceCode.call_args_list
    assert call(QOpenGLShader.Vertex, "vertex_code") in call_arg_list
    assert call(QOpenGLShader.Fragment, "fragment_code") in call_arg_list
    assert call(QOpenGLShader.Geometry, "geometry_code") in call_arg_list


def test_bindAndRelease():
    shader = ShaderProgram()

    mocked_shader_program = MagicMock()
    shader._shader_program = mocked_shader_program
    shader.bind()
    assert mocked_shader_program.bind.call_count == 1

    # Doing it without releasing in between shouldn't cause another bind.
    shader.bind()
    assert mocked_shader_program.bind.call_count == 1

    shader.release()
    assert mocked_shader_program.release.call_count == 1

    shader.release()
    assert mocked_shader_program.release.call_count == 1

    # We left it unbound, so now binding should work.
    shader.bind()
    assert mocked_shader_program.bind.call_count == 2