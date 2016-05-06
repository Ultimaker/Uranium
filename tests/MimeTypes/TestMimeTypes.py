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

def test_createMimeType():
    # Normal MIME type
    mime = MimeType(
        name = "application/x-test",
        comment = "Normal MIME type",
        suffixes = [ "tst" ]
    )
    assert mime.name == "application/x-test"
    assert mime.comment == "Normal MIME type"
    assert "tst" in mime.suffixes

    # No name.
    with pytest.raises(ValueError):
        mime = MimeType(
            name = None,
            comment = "Missing name",
            suffixes = [ "non" ]
        )

    # No suffixes.
    mime = MimeType(
        name = "application/x-no-suffixes",
        comment = "No Suffixes",
        suffixes = []
    )
    assert len(mime.suffixes) == 0

    # Multiple suffixes.
    mime = MimeType(
        name = "application/x-multiple",
        comment = "Multiple suffixes",
        suffixes = [ "boo", "baa" ]
    )
    assert "boo" in mime.suffixes
    assert "baa" in mime.suffixes

    # A preferred suffix.
    mime = MimeType(
        name = "application/x-preferred",
        comment = "Preferred suffix",
        suffixes = [ "boo", "baa" ],
        preferred_suffix = "baa"
    )
    assert mime.preferredSuffix == "baa"

    # Nonexistent preference.
    with pytest.raises(ValueError):
        mime = MimeType(
            name = "application/x-nonexistent-pref",
            comment = "Nonexistent preferred suffix",
            suffixes = [ "boo", "baa" ],
            preferred_suffix = "bee" # Not in the list of suffixes.
        )

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

