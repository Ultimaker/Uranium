# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pytest
import os.path

from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase

@pytest.fixture
def mime_database():
    MimeTypeDatabase._MimeTypeDatabase__custom_mimetypes = []
    mime = MimeType(
        name = "application/x-test",
        comment = "Test Mimetype",
        suffixes = [ "test" ]
    )
    MimeTypeDatabase.addMimeType(mime)
    mime = MimeType(
        name = "application/x-long-test",
        comment = "Long Test Mimetype",
        suffixes = [ "long.test" ]
    )
    MimeTypeDatabase.addMimeType(mime)
    return MimeTypeDatabase

def test_system_mimetypes(mime_database):
    mime = mime_database.getMimeTypeForFile(os.path.abspath(__file__))
    assert mime.name == "text/x-python"
    assert mime.comment == "Python script"
    assert mime.suffixes == ["py", "pyx", "wsgi"]
    assert mime.preferredSuffix == "py"

def test_compare(mime_database):
    mime1 = mime_database.getMimeType("text/plain")
    mime2 = mime_database.getMimeType("text/plain")

    assert id(mime1) != id(mime2)
    assert mime1 == mime2

def test_custom_mimetypes(mime_database):
    mime = mime_database.getMimeTypeForFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.test"))
    assert mime.name == "application/x-test"

    mime = mime_database.getMimeTypeForFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.long.test"))
    assert mime.name == "application/x-long-test"

def test_stripExtension(mime_database):
    mime = mime_database.getMimeTypeForFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.test"))

    assert mime.stripExtension("file.test") == "file"
    assert mime.stripExtension("file.long.test") == "file.long"
    assert mime.stripExtension("some.random.file.txt") == "some.random.file.txt"

    mime = mime_database.getMimeTypeForFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.long.test"))

    assert mime.stripExtension("file.test") == "file.test"
    assert mime.stripExtension("file.long.test") == "file"
    assert mime.stripExtension("some.random.file.txt") == "some.random.file.txt"

