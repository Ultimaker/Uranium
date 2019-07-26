import pytest
from unittest.mock import patch, MagicMock

from UM.FileHandler.FileHandler import FileHandler


@pytest.fixture
def file_handler(application):
    FileHandler._FileHandler__instance = None
    with patch("UM.FileHandler.FileHandler.PluginRegistry.addType"):
        handler = FileHandler(application, writer_type= "test_writer", reader_type= "test_reader")
    return handler


def test_getSupportedFileTypesRead(file_handler):
    registry = MagicMock()
    registry.getAllMetaData = MagicMock(return_value = [{"test_reader": [{"extension":".test"}]}])
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value = registry)):
        assert file_handler.getSupportedFileTypesRead() == {".test": ".test"}


def test_getSupportedFileTypesWrite(file_handler):
    registry = MagicMock()
    registry.getAllMetaData = MagicMock(return_value=[{"id":"beep", "test_writer":{ "output": [{ "extension": ".test", "mime_type": "test/test"}] }}])
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value=registry)):
        print(file_handler.getSupportedFileTypesWrite())
        assert file_handler.getSupportedFileTypesWrite() == [{'id': 'beep', 'extension': '.test', 'description': '.test', 'mime_type': 'test/test', 'mode': 1, 'hide_in_file_dialog': False}]