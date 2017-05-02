import os.path

import OBJReader

test_path = os.path.join(os.path.dirname(OBJReader.__file__), "tests")

def test_readOBJ():
    reader = OBJReader.OBJReader()
    sphere_file = os.path.join(test_path, "sphere.obj")
    result = reader.read(sphere_file)

    assert result  # It must return a node
    assert result.getMeshData()  # It should have mesh data
    assert result.getMeshData().getVertexCount() == 3840
    assert result.getMeshData().getFaceCount() == 1280
    assert result.getMeshData().hasNormals()  # It should have normals.