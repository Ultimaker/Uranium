# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import re #To replace parts of version strings with regex.
from typing import cast, Union

##  Represents a version number, like "3.2.8" and allows comparison of those
#   numbers.
class Version:
    ##  Constructs the version instance from a string representing the version.
    #
    #   The string representation may have dashes or underscores that separate
    #   the major, minor and revision version numbers. All text is ignored.
    #
    #   \param version A string or bytes representing a version number.
    def __init__(self, version: Union[str, bytes]) -> None:
        super().__init__()

        if type(version) == bytes:
            version = cast(bytes, version)
            version = version.decode("utf-8")

        if isinstance(version, str):
            version = cast(str, version)
            # Versions are in (MOD-)x.x.x(-x) format.
            version = version.replace("MOD-", "")
            version = version.replace("-", ".")
            version = version.replace("_", ".")
            version = version.replace("\"", "")
            version = re.sub(r"[A-Z]+", "", version)
            version_list = version.split(".")
        elif isinstance(version, list):
            version_list = version
        else:
            version_list = []

        self._major = 0
        self._minor = 0
        self._revision = 0
        try:
            self._major = int(version_list[0])
            self._minor = int(version_list[1])
            self._revision = int(version_list[2])
        except IndexError:
            pass
        except ValueError:
            pass

    ##  Gets the major version number.
    #
    #   The major version number is the first number of the version: "3" in the
    #   version "3.2.8".
    def getMajor(self) -> int:
        return self._major

    ##  Gets the minor version number.
    #
    #   The minor version number is the second number of the version: "2" in the
    #   version "3.2.8".
    def getMinor(self) -> int:
        return self._minor

    ##  Gets the revision or patch version number.
    #
    #   The revision version number is the third number of the version: "8" in
    #   the version "3.2.8".
    def getRevision(self) -> int:
        return self._revision

    ##  Indicates whether this version is later than the specified version.
    #
    #   Implements the > operator.
    #   \param other Either another version object or a string representing one.
    def __gt__(self, other: Union["Version", str]) -> bool:
        if isinstance(other, Version):
            return other.__lt__(self)
        elif isinstance(other, str):
            return Version(other).__lt__(self)
        else:
            return False

    ##  Indicates whether this version is earlier than the specified version.
    #
    #   Implements the < operator.
    #   \param other Either another version object or a string representing one.
    def __lt__(self, other: Union["Version", str]) -> bool:
        if isinstance(other, Version):
            if self._major < other.getMajor():
                return True
            if self._minor < other.getMinor() and self._major == other.getMajor():
                return True
            if self._revision < other.getRevision() and self._major == other.getMajor() and self._minor == other.getMinor():
                return True
            return False
        elif isinstance(other, str):
            return self < Version(other)
        else:
            return False

    ##  Indicates whether this version is equal to the specified version.
    #
    #   Implements the == operator.
    #   \param other Either another version object or a string representing one.
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._major == other.getMajor() and self._minor == other.getMinor() and self._revision == other.getRevision()
        elif isinstance(other, str):
            return self == Version(other)
        else:
            return False

    ##  Indicates whether this version is later or equal to the specified
    #   version.
    #
    #   Implements the >= operator.
    #   \param other Either another version object or a string representing one.
    def __ge__(self, other: Union["Version", str]) -> bool:
        return self.__gt__(other) or self.__eq__(other)

    ##  Indicates whether this version is earlier or equal to the specified
    #   version.
    #
    #   Implements the <= operator.
    #   \param other Either another version object or a string representing one.
    def __le__(self, other: Union["Version", str]) -> bool:
        return self.__lt__(other) or self.__eq__(other)

    ##  Returns a string representation containing the major, minor and revision
    #   number.
    #
    #   Such as "3.2.8".
    def __str__(self) -> str:
        return "%s.%s.%s" %(self._major, self._minor, self._revision)

    ##  Returns a number reasonably representing the identity of the version.
    def __hash__(self) -> int:
        return hash(self.__str__())
