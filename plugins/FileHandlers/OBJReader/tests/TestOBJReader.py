import os.path

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pytest
from unittest.mock import patch

import OBJReader

test_path = os.path.join(os.path.dirname(OBJReader.__file__), "tests")


def test_readOBJ():
    reader = OBJReader.OBJReader()
    sphere_file = os.path.join(test_path, "sphere.obj")
    with patch("UM.Application.Application.getInstance"):
        result = reader.read(sphere_file)

    assert result  # It must return a node
    assert result.getMeshData()  # It should have mesh data
    assert result.getMeshData().getVertexCount() == 3840
    assert result.getMeshData().getFaceCount() == 1280
    assert result.getMeshData().hasNormals()  # It should have normals.

@pytest.mark.parametrize("filename", [
    "vertex_duplicated.obj",
    "vertex_indexed.obj",
    "vertex_normal_indexed.obj",
    "vertex_texture_indexed.obj",
    "vertex_texture_normal_indexed.obj",
    "negative_indexed.obj",
    "negative_interweaved.obj"
])
def test_cubes(filename):
    """
    Tests reading cubes in various formats. All of them render the same cube in the end.
    """
    reader = OBJReader.OBJReader()
    path = os.path.join(test_path, filename)
    with patch("UM.Application.Application.getInstance"):
        result = reader.read(path)

    mesh = result.getMeshData()
    assert mesh.getFaceCount() == 6 * 2
    assert mesh.getVertexCount() == mesh.getFaceCount() * 3  # We need to serialise them as separate triangles, not sharing indices.

    # All of these triangles must be present in the mesh.
    assert isTriangleInMesh([[0, 0, 0], [0, 10, 0], [0, 0, -10]], mesh)  # Small X.
    assert isTriangleInMesh([[0, 10, 0], [0, 10, -10], [0, 0, -10]], mesh)
    assert isTriangleInMesh([[10, 0, 0], [10, 0, -10], [10, 10, -10]], mesh)  # Large X.
    assert isTriangleInMesh([[10, 0, 0], [10, 10, -10], [10, 10, 0]], mesh)
    assert isTriangleInMesh([[0, 0, 0], [0, 0, -10], [10, 0, -10]], mesh)  # Small Y.
    assert isTriangleInMesh([[0, 0, 0], [10, 0, -10], [10, 0, 0]], mesh)
    assert isTriangleInMesh([[0, 10, 0], [10, 10, 0], [0, 10, -10]], mesh)  # Large Y.
    assert isTriangleInMesh([[10, 10, 0], [10, 10, -10], [0, 10, -10]], mesh)
    assert isTriangleInMesh([[0, 0, 0], [10, 0, 0], [10, 10, 0]], mesh)  # Small Z.
    assert isTriangleInMesh([[0, 0, 0], [10, 10, 0], [0, 10, 0]], mesh)
    assert isTriangleInMesh([[10, 0, -10], [0, 0, -10], [0, 10, -10]], mesh)  # Large Z.
    assert isTriangleInMesh([[10, 0, -10], [0, 10, -10], [10, 10, -10]], mesh)

def isTriangleInMesh(triangle, mesh_data):
    """
    Tests if a triangle is present in mesh data.
    :param triangle: The triangle, as list of 3 lists of X, Y and Z coordinates.
    :param mesh_data: A MeshData object.
    :return: True if the triangle is present in the mesh, or False if it isn't.
    """
    vertices = mesh_data.getVertices()
    for face in mesh_data.getIndices():
        for rotation in (0, 1, 2):  # Doesn't matter where the triangle starts. Try all 3 rotations.
            if list(vertices[face[0]]) == triangle[(0 + rotation) % 3] and list(vertices[face[1]]) == triangle[(1 + rotation) % 3] and list(vertices[face[2]]) == triangle[(2 + rotation) % 3]:
                return True
    return False  # Not found.