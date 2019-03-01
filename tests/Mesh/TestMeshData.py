import numpy

from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData
from UM.Math.Matrix import Matrix


def test_transformMeshData():
    transformation_matrix = Matrix()
    transformation_matrix.setByTranslation(Vector(30, 20, 10))

    vertices = numpy.zeros((1, 3), dtype=numpy.float32)
    mesh_data = MeshData(vertices)

    transformed_mesh = mesh_data.getTransformed(transformation_matrix)

    assert transformed_mesh.getVertex(0)[0] == 30.
    assert transformed_mesh.getVertex(0)[1] == 20.
    assert transformed_mesh.getVertex(0)[2] == 10.


def test_getExtents():
    # Create a cube mesh at position 0,0,0
    builder = MeshBuilder()
    builder.addCube(20, 20, 20)
    mesh_data = builder.build()

    extents = mesh_data.getExtents()
    assert extents.width == 20
    assert extents.height == 20
    assert extents.depth == 20

    assert extents.maximum == Vector(10, 10, 10)
    assert extents.minimum == Vector(-10, -10, -10)


def test_getExtentsTransposed():
    # Create a cube mesh at position 0,0,0
    builder = MeshBuilder()
    builder.addCube(20, 20, 20)
    mesh_data = builder.build()

    transformation_matrix = Matrix()
    transformation_matrix.setByTranslation(Vector(10, 10, 10))

    extents = mesh_data.getExtents(transformation_matrix)
    assert extents.width == 20
    assert extents.height == 20
    assert extents.depth == 20

    assert extents.maximum == Vector(20, 20, 20)
    assert extents.minimum == Vector(0, 0, 0)