import os.path

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from unittest.mock import patch
import STLReader
from UM.Mesh.MeshBuilder import MeshBuilder

test_path = os.path.join(os.path.dirname(STLReader.__file__), "tests")


def test_readASCII():
    reader = STLReader.STLReader()
    ascii_path = os.path.join(test_path, "simpleTestCubeASCII.stl")
    with patch("UM.Application.Application.getInstance"):
        result = reader.read(ascii_path)
    assert result

    if STLReader.use_numpystl:
        # If the system the test runs on supports numpy stl, we should also check the non numpy stl option.
        f = open(ascii_path, "rt", encoding = "utf-8")
        mesh_builder = MeshBuilder()
        reader._loadAscii(mesh_builder, f)
        mesh_builder.calculateNormals(fast=True)

        assert mesh_builder.getVertexCount() != 0


def test_readBinary():
    reader = STLReader.STLReader()
    binary_path = os.path.join(test_path, "simpleTestCubeBinary.stl")
    with patch("UM.Application.Application.getInstance"):
        result = reader.read(binary_path)

    if STLReader.use_numpystl:
        # If the system the test runs on supporst numpy stl, we should also check the non numpy stl option.
        f = open(binary_path, "rb")
        mesh_builder = MeshBuilder()
        reader._loadBinary(mesh_builder, f)
        mesh_builder.calculateNormals(fast=True)

        assert mesh_builder.getVertexCount() != 0
    assert result

