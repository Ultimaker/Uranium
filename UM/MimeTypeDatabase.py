# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
from typing import cast, List, Optional

import magic


# Raised when a MIME type can not be found.
class MimeTypeNotFoundError(Exception):
    pass


# Simple value type class that encapsulates MIME type data.
class MimeType:
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
                if preferred_suffix not in self.__suffixes:
                    raise ValueError("Preferred suffix is not a valid suffix")
                self.__preferred_suffix = preferred_suffix
            else:
                self.__preferred_suffix = self.__suffixes[0]
        else:
            self.__preferred_suffix = ""

    @property
    def name(self) -> str:
        return self.__name

    @property
    def comment(self) -> str:
        return self.__comment

    @property
    def suffixes(self) -> List[str]:
        return self.__suffixes

    @property
    def preferredSuffix(self) -> str:
        return self.__preferred_suffix

    def __repr__(self) -> str:
        return "<MimeType name={0}>".format(self.__name)

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False
        other = cast(MimeType, other)
        return self.__name == other.name

    def stripExtension(self, file_name: str) -> str:
        for suffix in self.__suffixes:
            suffix = suffix.lower()
            if file_name.lower().endswith(suffix, file_name.find(".")):
                index = file_name.lower().rfind("." + suffix)
                return file_name[0:index]

        return file_name


class MimeTypeDatabase:

    @classmethod
    def getMimeType(cls, name: str) -> MimeType:
        for custom_mime in cls.__custom_mimetypes:
            if custom_mime.name == name:
                return custom_mime

        mime = magic.from_file(name, mime = True)
        return mime

    ##  Get a MIME type for a specific file.
    #
    #   \param file_name The name of the file to get the MIME type for.
    #   \return A MimeType object that contains the detected MIME type for the
    #   file.
    #   \exception MimeTypeNotFoundError Raised when no MIME type can be found
    #   for the specified file.
    @classmethod
    def getMimeTypeForFile(cls, file_path: str) -> MimeType:
        # Properly normalize the file name to only be the base name of a path if we pass a path.
        file_name = os.path.basename(os.path.realpath(file_path))

        matches = [] # type: List[MimeType]
        for mime_type in cls.__custom_mimetypes:
            # Check if the file name ends with the suffixes, starting at the first . encountered.
            # This means that "suffix" will not match, ".suffix" will and "suffix.something.suffix" will also match
            if file_name.lower().endswith(tuple(mime_type.suffixes), file_name.find(".")):
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

        mime_name = magic.from_file(file_path, mime = True)
        mime_description = magic.from_file(file_path)
        suffix = "." + file_name.lower().split(".")[-1]
        mime_type = MimeType(mime_name, mime_description, suffixes=[suffix])
        return mime_type

    ##  Add a custom MIME type that can be detected.
    #
    #   \param mime_type The custom MIME type to add.
    @classmethod
    def addMimeType(cls, mime_type: MimeType) -> None:
        cls.__custom_mimetypes.append(mime_type)

    __custom_mimetypes = []  # type: List[MimeType]
