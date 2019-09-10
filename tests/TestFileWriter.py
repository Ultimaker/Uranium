from UM.FileHandler.FileWriter import FileWriter
import pytest
import io

def test_getAddToRecentFiles():
    writer = FileWriter(add_to_recent_files = True)
    assert writer.getAddToRecentFiles()

    other_writer = FileWriter(add_to_recent_files = False)
    assert not other_writer.getAddToRecentFiles()


def test_write():
    writer = FileWriter()
    with pytest.raises(Exception):
        writer.write(io.StringIO(), "Some data to write")


def test_information():
    writer = FileWriter()
    writer.setInformation("Some information about the writer")
    assert writer.getInformation() == "Some information about the writer"