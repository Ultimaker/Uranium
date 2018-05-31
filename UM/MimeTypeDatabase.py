# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os.path
from PyQt5.QtCore import QMimeDatabase, QMimeType
from typing import cast, List, Optional

##  Raised when a MIME type can not be found.
class MimeTypeNotFoundError(Exception):
    pass

##  Simple value type class that encapsulates MIME type data.
class MimeType:
    ##  Constructor
    #
    #   \param name The MIME type name, like "text/plain".
    #   \param comment A description of the MIME type.
    #   \param suffixes A list of possible suffixes for the type.
    #   \param preferred_suffix The preferred suffix for the type. Defaults to
    #   ``suffixes[0]`` if not specified.
    def __init__(self, name: str, comment: str, suffixes: Optional[List[str]], preferred_suffix: str = None) -> None:
        if name is None:
            raise ValueError("Name cannot be None")

        if comment is None:
            raise ValueError("Comment cannot be None")

        self.__name = name
        self.__comment = comment
        self.__suffixes = suffixes if isinstance(suffixes, list) else []

        if self.__suffixes:
            if preferred_suffix:
                if not preferred_suffix in self.__suffixes:
                    raise ValueError("Preferred suffix is not a valid suffix")
                self.__preferred_suffix = preferred_suffix
            else:
                self.__preferred_suffix = self.__suffixes[0]
        else:
            self.__preferred_suffix = ""

    ##  The name that identifies the MIME type.
    @property
    def name(self) -> str:
        return self.__name

    ##  The comment that describes of the MIME type.
    @property
    def comment(self) -> str:
        return self.__comment

    ##  The list of file name suffixes for the MIME type.
    @property
    def suffixes(self) -> List[str]:
        return self.__suffixes

    ##  The preferred file name suffix for the MIME type.
    @property
    def preferredSuffix(self) -> str:
        return self.__preferred_suffix

    ##  Gives a programmer-readable representation of the MIME type.
    #
    #   \return A string representing the MIME type.
    def __repr__(self) -> str:
        return "<MimeType name={0}>".format(self.__name)

    ##  Indicates whether this MIME type is equal to another MIME type.
    #
    #   They are equal if the names match, since MIME types should have unique
    #   names.
    #
    #   \return ``True`` if the two MIME types are equal, or ``False``
    #   otherwise.
    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False
        other = cast(MimeType, other)
        return self.__name == other.name

    ##  Strip the extension from a file name when it corresponds to one of the
    #   suffixes of this MIME type.
    #
    #   \param file_name The file name to strip of extension.
    #   \return ``file_name`` without extension, or ``file_name`` when it does
    #   not match.
    def stripExtension(self, file_name: str) -> str:
        for suffix in self.__suffixes:
            if file_name.endswith(suffix, file_name.find(".")):
                index = file_name.rfind("." + suffix)
                return file_name[0:index]

        return file_name


    ##  Create a ``MimeType`` object from a ``QMimeType`` object.
    #
    #   \param qt_mime The ``QMimeType`` object to convert.
    #   \return A new ``MimeType`` object with properties equal to the
    #   ``QMimeType`` object.
    @staticmethod
    def fromQMimeType(qt_mime: QMimeType) -> "MimeType":
        return MimeType(
            name = qt_mime.name(),
            comment = qt_mime.comment(),
            suffixes = qt_mime.suffixes(),
            preferred_suffix = qt_mime.preferredSuffix()
        )

##  Handles lookup of MIME types for files with support for custom MIME types.
#
#   This class wraps around ``QMimeDatabase`` and extends it with support for
#   custom MIME types defined at runtime.
#
#   \note Custom MIME types are currently only detected based on extension.
class MimeTypeDatabase:
    ##  Get a MIME type by name.
    #
    #   This will return a ``MimeType`` object corresponding to the specified
    #   name.
    #
    #   \param name The name of the MIME type to return.
    #   \return A ``MimeType`` object corresponding to the specified name.
    #
    #   \exception MimeTypeNotFoundError Raised when the specified MIME type
    #   cannot be found.
    @classmethod
    def getMimeType(cls, name: str) -> MimeType:
        for custom_mime in cls.__custom_mimetypes:
            if custom_mime.name == name:
                return custom_mime

        mime = cls.__system_database.mimeTypeForName(name)
        if mime.isValid():
            return MimeType.fromQMimeType(mime)

        raise MimeTypeNotFoundError("Could not find mime type named {0}".format(name))

    MimeTypeNotFoundError = MimeTypeNotFoundError

    ##  Get a MIME type for a specific file.
    #
    #   \param file_name The name of the file to get the MIME type for.
    #   \return A MimeType object that contains the detected MIME type for the
    #   file.
    #   \exception MimeTypeNotFoundError Raised when no MIME type can be found
    #   for the specified file.
    @classmethod
    def getMimeTypeForFile(cls, file_name: str) -> MimeType:
        # Properly normalize the file name to only be the base name of a path if we pass a path.
        file_name = os.path.basename(os.path.realpath(file_name))

        matches = [] # type: List[MimeType]
        for mime_type in cls.__custom_mimetypes:
            # Check if the file name ends with the suffixes, starting at the first . encountered.
            # This means that "suffix" will not match, ".suffix" will and "suffix.something.suffix" will also match
            if file_name.endswith(tuple(mime_type.suffixes), file_name.find(".")):
                matches.append(mime_type)

        if len(matches) > 1:
            longest_suffix = ""
            longest_mime = None
            for match in matches:
                max_suffix = max(match.suffixes)
                if len(max_suffix) > len(longest_suffix):
                    longest_suffix = max_suffix
                    longest_mime = match
            return cast(MimeType, longest_mime)
        elif matches:
            return matches[0]

        mime = cls.__system_database.mimeTypeForFile(file_name)
        if not mime.isDefault() and mime.isValid():
            return MimeType.fromQMimeType(mime)

        raise MimeTypeNotFoundError("Could not find a valid MIME type for {0}".format(file_name))

    ##  Add a custom MIME type that can be detected.
    #
    #   \param mime_type The custom MIME type to add.
    @classmethod
    def addMimeType(cls, mime_type: MimeType) -> None:
        cls.__custom_mimetypes.append(mime_type)

    __system_database = QMimeDatabase()
    __custom_mimetypes = [] # type: List[MimeType]
