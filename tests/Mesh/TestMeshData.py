import numpy

from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData, MeshType
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


def test_attributes():
    attributes = { "test": {
                "value": [10],
                "derp": "OMG"
                }}
    mesh_data = MeshData(attributes = attributes)

    assert mesh_data.hasAttribute("test")
    assert mesh_data.getAttribute("test") == { "value": [10], "derp": "OMG" }

    assert mesh_data.attributeNames() == ["test"]


def test_hasData():
    # Simple test to see if the has whatever functions do their job correctly

    empty_mesh = MeshData()

    assert not empty_mesh.hasNormals()
    assert not empty_mesh.hasColors()
    assert not empty_mesh.hasUVCoordinates()
    assert not empty_mesh.hasIndices()

    filled_mesh = MeshData(normals = [], colors = [], uvs = [], indices=[])
    assert filled_mesh.hasNormals()
    assert filled_mesh.hasColors()
    assert filled_mesh.hasUVCoordinates()
    assert filled_mesh.hasIndices()


def test_counts():
    empty_mesh = MeshData()

    assert empty_mesh.getFaceCount() == 0
    assert empty_mesh.getVertexCount() == 0

    filled_mesh = MeshData(indices = numpy.zeros((5, 3), dtype=numpy.float32), vertices = numpy.zeros((12, 3), dtype=numpy.float32))

    assert filled_mesh.getFaceCount() == 5
    assert filled_mesh.getVertexCount() == 12


def test_getPositionAndType():
    mesh_data = MeshData(zero_position=Vector(0, 12, 13), center_position=Vector(10, 20, 30), type = MeshType.pointcloud)
    assert mesh_data.getZeroPosition() == Vector(0, 12, 13)
    assert mesh_data.getCenterPosition() == Vector(10, 20, 30)
    assert mesh_data.getType() == MeshType.pointcloud