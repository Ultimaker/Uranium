import pytest
from unittest.mock import patch, MagicMock

from UM.FileHandler.FileHandler import FileHandler


@pytest.fixture
def file_handler(application):
    FileHandler._FileHandler__instance = None
    with patch("UM.FileHandler.FileHandler.PluginRegistry.addType"):
        handler = FileHandler(application, writer_type= "test_writer", reader_type= "test_reader")
    return handler

@pytest.fixture
def file_writer():
    mocked_writer = MagicMock()
    mocked_writer.getPluginId = MagicMock(return_value="beep")
    return mocked_writer


def test_getSupportedFileTypesRead(file_handler):
    registry = MagicMock()
    registry.getAllMetaData = MagicMock(return_value = [{"test_reader": [{"extension":".test"}]}])
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value = registry)):
        assert file_handler.getSupportedFileTypesRead() == {".test": ".test"}


def test_getSupportedFileTypesWrite(file_handler):
    registry = MagicMock()
    registry.getAllMetaData = MagicMock(return_value=[{"id":"beep", "test_writer":{ "output": [{ "extension": ".test", "mime_type": "test/test"}] }}])
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value=registry)):
        assert file_handler.getSupportedFileTypesWrite() == [{'id': 'beep', 'extension': '.test', 'description': '.test', 'mime_type': 'test/test', 'mode': 1, 'hide_in_file_dialog': False}]


def test_getWriterByMimeType_KnownMimeType(file_handler, file_writer):
    file_handler.addWriter(file_writer)
    registry = MagicMock()
    registry.getAllMetaData = MagicMock(return_value=[{"id": "beep", "test_writer": {"output": [{"extension": ".test", "mime_type": "test/test"}]}}])
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value=registry)):
        assert file_handler.getWriterByMimeType("test/test") == file_writer


def test_getWriterByMimeType_UnknownMimeType(file_handler, file_writer):
    file_handler.addWriter(file_writer)
    registry = MagicMock()
    registry.getAllMetaData = MagicMock(return_value=[])
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value=registry)):
        assert file_handler.getWriterByMimeType("test/test") is None


def test_getWriter_KnownWriter(file_handler, file_writer):
    file_handler.addWriter(file_writer)
    assert file_handler.getWriter("beep") == file_writer


def test_getWriter_UnknownWriter(file_handler):
    # We never added a writer, so we should get None
    assert file_handler.getWriter("beep") is None


def test_getReaderForFile(file_handler):
    mocked_reader = MagicMock()
    mocked_reader.acceptsFile = MagicMock(return_value = True)
    file_handler.addReader(mocked_reader)

    assert file_handler.getReaderForFile("whatever") is mocked_reader


def test_getReaderForFileWithException(file_handler):
    mocked_reader = MagicMock()
    mocked_reader.acceptsFile = MagicMock(side_effect=Exception)
    file_handler.addReader(mocked_reader)

    # As file readers are plugins, we ensure that any exceptions are handled and dropped so they don't crash the
    # application
    assert file_handler.getReaderForFile("whatever") is None
