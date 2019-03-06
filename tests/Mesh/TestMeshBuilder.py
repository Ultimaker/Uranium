import numpy

from UM.Math.Color import Color
from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder


def test_addVertexWithNormal():
    builder = MeshBuilder()
    builder.addVertexWithNormal(10, 20, 30, -1, -2, -3)

    assert builder.getVertex(0)[0] == 10
    assert builder.getVertex(0)[1] == 20
    assert builder.getVertex(0)[2] == 30

    assert builder.hasNormals()  # We just added a vert with a normal, so we should have em
    assert builder.getNormals()[0][0] == -1
    assert builder.getNormals()[0][1] == -2
    assert builder.getNormals()[0][2] == -3

    assert builder.getVertexCount() == 1
    # There is only one vertex, so we should get None back
    assert builder.getVertex(22) is None


def test_addFace():
    builder = MeshBuilder()
    builder.addFaceByPoints(0, 0, 0, 10, 0, 0, 10, 10, 0)

    assert builder.getVertexCount() == 3
    assert builder.getFaceCount() == 1
    assert not builder.hasNormals()
    # Check if all the data ended up where it should be
    assert builder.getVertex(0)[0] == 0
    assert builder.getVertex(0)[1] == 0
    assert builder.getVertex(0)[2] == 0

    assert builder.getVertex(1)[0] == 10
    assert builder.getVertex(1)[1] == 0
    assert builder.getVertex(1)[2] == 0

    assert builder.getVertex(2)[0] == 10
    assert builder.getVertex(2)[1] == 10
    assert builder.getVertex(2)[2] == 0


def test_addFaceWithNormals():
    builder = MeshBuilder()
    builder.addFaceWithNormals(0, 0, 0, 1, 0, 0, 10, 0, 0, 0, 1, 0, 10, 10, 0, 0, 0, 1)
    assert builder.getVertexCount() == 3
    assert builder.getFaceCount() == 1
    assert builder.hasNormals()


def test_setVertexColor():
    builder = MeshBuilder()
    builder.addVertex(1, 2, 3)
    builder.setVertexColor(0, Color(1.0, 0.5, 0.2))
    assert builder.hasColors()
    assert builder.getColors()[0][0] == 1.0


def test_calculateNormals():
    builder = MeshBuilder()
    # Builder shouldn't start off with normals
    assert not builder.hasNormals()
    # Ensure that if there are no vertices / faces that calling the calculate doesn't break anything.
    builder.calculateNormals()
    assert not builder.hasNormals()

    builder.addFaceByPoints(0, 0, 0, 10, 0, 0, 10, 10, 0)

    builder.calculateNormals()
    assert builder.hasNormals()
    assert numpy.array_equal(builder.getNormals(), numpy.array([[0., 0., 1.], [0., 0., 1.], [0., 0., 1.]]))

    builder2 = MeshBuilder()
    builder2.addFaceByPoints(0, 0, 0, 0, 10, 0, 0, 10, 10)
    builder2.calculateNormals(fast = True)
    assert numpy.array_equal(builder2.getNormals(), numpy.array([[1., 0., 0], [1., 0., 0.], [1., 0., 0.]]))


def test_addLine():
    builder = MeshBuilder()
    builder.addLine(Vector(0, 0, 0), Vector(10, 11, 12))

    assert builder.getVertexCount() == 2
    assert builder.getVertex(1)[0] == 10
    assert builder.getVertex(1)[1] == 11
    assert builder.getVertex(1)[2] == 12


def test_addLineWithColor():
    builder = MeshBuilder()
    builder.addLine(Vector(0, 0, 0), Vector(10, 11, 12), Color(1.0, 0.5, 0.25))

    assert builder.getColors()[0][0] == 1.0
    assert builder.getColors()[0][1] == 0.5
    assert builder.getColors()[0][2] == 0.25

    assert builder.getColors()[1][0] == 1.0
    assert builder.getColors()[1][1] == 0.5
    assert builder.getColors()[1][2] == 0.25


def test_reserveFaceCount():
    builder = MeshBuilder()
    builder.addVertex(1, 2, 3)

    builder.reserveFaceCount(200)
    # Reserving face count should reset the verts
    assert builder.getVertexCount() == 0


def test_reserveFaceAndVertexCount():
    builder = MeshBuilder()
    builder.addVertex(1, 2, 3)

    builder.reserveFaceAndVertexCount(200, 20)
    # Reserving face count should reset the verts
    assert builder.getVertexCount() == 0


def test_reserveVertexCount():
    builder = MeshBuilder()
    builder.addVertex(1, 2, 3)

    builder.reserveVertexCount(10)
    # Reserving face count should reset the verts
    assert builder.getVertexCount() == 0