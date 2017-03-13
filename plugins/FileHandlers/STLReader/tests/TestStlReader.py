import os.path
import pytest

import STLReader

def test_read():
    reader = STLReader.STLReader()
    result = reader.read(os.path.join(os.path.dirname(STLReader.__file__), "simpleTestCube.stl"))

    assert result
