# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest
import os.path
import PyQt5.QtCore # For the test of converting QMimeType to MimeType.

from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase, MimeTypeNotFoundError

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
    mime = MimeType(
        name = "application/x-multiple-test",
        comment = "Multiple Extension MIME Type",
        suffixes = [ "tost", "ost" ],
        preferred_suffix = "ost"
    )
    MimeTypeDatabase.addMimeType(mime)
    mime = MimeType(
        name = "image/jpeg",
        comment = "Custom JPEG MIME Type",
        suffixes = [ "jpg", "jpeg" ],
        preferred_suffix = "jpg"
    )
    MimeTypeDatabase.addMimeType(mime)

    return MimeTypeDatabase

def test_system_mimetypes(mime_database):
    mime = mime_database.getMimeTypeForFile(os.path.abspath(__file__))
    assert mime.name == "text/x-python"
    assert mime.comment == "Python script"
    assert "py" in mime.suffixes
    assert mime.preferredSuffix == "py"

def test_compare(mime_database):
    mime1 = mime_database.getMimeType("text/plain")
    mime2 = mime_database.getMimeType("text/plain")

    assert id(mime1) != id(mime2)
    assert mime1 == mime2

##  Tests the creation of new MIME types.
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

##  Tests creating a MIME type from a QMimeType object.
def test_fromQMimeType():
    database = PyQt5.QtCore.QMimeDatabase()
    qmime = database.mimeTypeForFile(PyQt5.QtCore.QFileInfo(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.png"))) # Obtain some MIME type from the database (most likely image/png).
    mime = MimeType.fromQMimeType(qmime)
    assert mime.name == qmime.name()
    assert mime.comment == qmime.comment()
    assert len(mime.suffixes) == len(qmime.suffixes())
    for suffix in qmime.suffixes():
        assert suffix in mime.suffixes
    assert mime.preferredSuffix == qmime.preferredSuffix()

##  Tests the querying for MIME types by name.
#
#   \param mime_database A MIME type database from a fixture.
def test_getMimeType(mime_database):
    mime = mime_database.getMimeType("application/x-test") # Easy case.
    assert mime.comment == "Test Mimetype"

    mime = mime_database.getMimeType("image/jpeg")
    assert mime.comment == "Custom JPEG MIME Type" # We must get the custom one, not Qt's MIME type.

    mime = mime_database.getMimeType("image/png")
    assert mime.comment == "PNG image" # Qt's MIME type (at least on my system).

    with pytest.raises(MimeTypeNotFoundError):
        mime_database.getMimeType("archive/x-file-that-your-mom-would-fit-in") # Try to fetch some non-existing MIME type.


##  Data for test_getMimeTypeForFile
#
#   Each entry consists of a dict, with the following values:
#   * path: Required. The path to check the mime type for.
#   * expect_fail: Default False. Expect this entry to raise an error, so handle it appropriately. Will ignore all other properties.
#   * description: Ignored. Used to have a human-readable description of the test data.
#   All other entries in the dict will be checked as properties on the mime type object. For example, name = "test" will be checked
#   that there is a "name" property on the mime type object that has the value "test".
path_base = os.path.dirname(os.path.abspath(__file__))
test_getMimeTypeForFile_data = [
    dict(path = os.path.join(path_base, "test.jpg"), comment = "Custom JPEG MIME Type", description = "Customized Mime Types should override system mime types"),
    dict(path = os.path.join(path_base, "test.png"), name = "image/png", description = "Valid Mime Types should return the proper system mime type"),
    dict(path = os.path.join(path_base, "file.test"), name = "application/x-test", description = "New mime types should return the right values"),
    dict(path = os.path.join(path_base, "file.long.test"), name = "application/x-long-test", description = "Multiple matches should prefer the longest match"),
    dict(path = os.path.join(path_base, "filetest.test.test"), name = "application/x-test", description = "Files with double extensions should still match"),
    dict(path = os.path.join(path_base, ".test"), name = "application/x-test", description = "Files with only an extension should still match"),
    dict(path = os.path.join(path_base, "pink.unicorn"), expect_fail = True, description = "Unknown types should generate an error"),
    dict(path = os.path.join(path_base, "filetest"), expect_fail = True, description = "File names with no extension should not match"),
    # Same test but without absolute path.
    dict(path = "test.jpg", comment = "Custom JPEG MIME Type", description = "Customized Mime Types should override system mime types"),
    dict(path = "test.png", name = "image/png", description = "Valid Mime Types should return the proper system mime type"),
    dict(path = "file.test", name = "application/x-test", description = "New mime types should return the right values"),
    dict(path = "file.long.test", name = "application/x-long-test", description = "Multiple matches should prefer the longest match"),
]

##  Tests the querying for MIME types for opening a specific file.
#
#   \param mime_database A MIME type database from a fixture.
#   \param data Test data supplied by pytest, see above.
@pytest.mark.parametrize("data", test_getMimeTypeForFile_data)
def test_getMimeTypeForFile(mime_database, data):
    data.pop("description")
    file_path = data.pop("path")
    expect_fail = data.pop("expect_fail", False)
    if not expect_fail:
        mime = mime_database.getMimeTypeForFile(file_path)
        for key, value in data.items():
            assert getattr(mime, key) == value
    else:
        with pytest.raises(MimeTypeNotFoundError):
            mime_database.getMimeTypeForFile(file_path)

##  Tests the utility function that strips a MIME type's extension from a
#   filename.
#
#   \param mime_database A new MIME type database from a fixture, which is
#   already filled with a few MIME types.
def test_stripExtension(mime_database):
    mime = mime_database.getMimeTypeForFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.test"))
    assert mime.stripExtension("file.test") == "file"
    assert mime.stripExtension("file.long.test") == "file.long"
    assert mime.stripExtension("some.random.file.txt") == "some.random.file.txt"
    assert mime.stripExtension("filetest") == "filetest" # Filename happens to end with the extension, but it's not the file's extension since there is no period before it.
    assert mime.stripExtension("file.test.cfg.test") == "file.test.cfg" # Extension and period occurs earlier in the filename as well.

    mime = mime_database.getMimeTypeForFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.long.test"))
    assert mime.stripExtension("file.test") == "file.test"
    assert mime.stripExtension("file.long.test") == "file"
    assert mime.stripExtension("some.random.file.txt") == "some.random.file.txt"

    mime = mime_database.getMimeTypeForFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.tost"))
    assert mime.stripExtension("file.tost") == "file"
    assert mime.stripExtension("file.ost") == "file"
    assert mime.stripExtension("file.tost.png") == "file.tost.png"
