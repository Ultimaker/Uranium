# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QMimeDatabase

from UM.Decorators import ascopy

##  Raised when a mime type can not be found.
class MimeTypeNotFoundError(Exception):
    pass

##  Simple value type class that encapsulates mime type data.
class MimeType:
    ##  Constructor
    #
    #   \param name The mime type name, like "text/plain".
    #   \param comment A description of the mime type.
    #   \param suffixes A list of possible suffixes for the type.
    #   \param preferred_suffix The preferred suffix for the type. Defaults to suffixes[0] if not specified.
    def __init__(self, name, comment, suffixes, preferred_suffix = None):
        self._name = name
        self._comment = comment
        self._suffixes = suffixes
        self._preferred_suffix = preferred_suffix if preferred_suffix else suffixes[0]

    ##  The name of the mime type.
    @property
    def name(self):
        return self._name

    ##  The comment of the mime type.
    @property
    def comment(self):
        return self._comment

    ##  The list of suffixes for the mime type.
    @property
    def suffixes(self):
        return self._suffixes

    ##  The preferred suffix for the mime type.
    @property
    def preferredSuffix(self):
        return self._preferred_suffix

    def __repr__(self):
        return "<MimeType name={0}>".format(self._name)

    def __eq__(self, other):
        return self._name == other.name

    ##  Strip the extension from a file name when it corresponds to one of the suffixes of this mime type.
    #
    #   \param file_name The file name to strip of extension.
    #
    #   \return file_name without extension or file_name when it does not match.
    def stripExtension(self, file_name):
        candidates = []
        for suffix in self._suffixes:
            if file_name.endswith(suffix):
                candidates.append(suffix)

        if candidates:
            longest_suffix = max(candidates)
            return file_name.replace("." + longest_suffix, "")
        else:
            return file_name

    ##  Create a MimeType object from a QMimeType object.
    #
    #   \param qt_mime The QMimeType object to convert.
    #
    #   \return A new MimeType object with properties equal to the QMimeType object.
    @staticmethod
    def fromQMimeType(qt_mime):
        return MimeType(
            name = qt_mime.name(),
            comment = qt_mime.comment(),
            suffixes = qt_mime.suffixes(),
            preferred_suffix = qt_mime.preferredSuffix()
        )

##  Handles lookup of mime types for files with support for custom mime types.
#
#   This class wraps around QMimeDatabase and extends it with support for custom
#   mime types defined at runtime.
#
#   \note Custom mime types are currently only detected based on extension.
class MimeTypeDatabase:
    ##  Get a mime type by name
    #
    #   This will return a MimeType object corresponding to the specified name.
    #
    #   \param name The name of the mime type to return.
    #
    #   \return A MimeType object corresponding to the specified name.
    #
    #   \exception MimeTypeNotFoundError Raised when the specified mime type cannot be found.
    @classmethod
    @ascopy
    def getMimeType(cls, name):
        for mime in cls.__custom_mimetypes:
            if mime.name == name:
                return mime

        mime = cls.__system_database.mimeTypeForName(name)
        if mime.isValid():
            return MimeType.fromQMimeType(mime)

        raise MimeTypeNotFoundError("Could not find mime type named {0}".format(name))

    ##  Get a mime type for a specific file.
    #
    #   \param file_name The name of the file to get the mime type for.
    #
    #   \return A MimeType object that contains the detected mime type for the file.
    #
    #   \exception MimeTypeNotFoundError Raised when no mime type can be found for the specified file.
    @classmethod
    @ascopy
    def getMimeTypeForFile(cls, file_name):
        matches = []
        for mime_type in cls.__custom_mimetypes:
            if file_name.endswith(tuple(mime_type.suffixes)):
                matches.append(mime_type)

        if len(matches) > 1:
            longest_suffix = None
            longest_mime = None
            for match in matches:
                max_suffix = max(match.suffixes)
                if not longest_suffix or len(max_suffix) > len(longest_suffix):
                    longest_suffix = max_suffix
                    longest_mime = match
            return longest_mime
        elif matches:
            return matches[0]

        mime = cls.__system_database.mimeTypeForFile(file_name)
        if not mime.isDefault() and mime.isValid():
            return MimeType.fromQMimeType(mime)

        raise MimeTypeNotFoundError("Could not find a valid mime type for {0}".format(file_name))

    ##  Add a custom mime type that can be detected.
    #
    #   \param mime_type \type{MimeType} The custom mime type to add.
    @classmethod
    def addMimeType(cls, mime_type):
        cls.__custom_mimetypes.append(mime_type)

    __system_database = QMimeDatabase()
    __custom_mimetypes = []
