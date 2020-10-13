# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import re  # To replace parts of version strings with regex.
from typing import cast, Union, List
from UM.Logger import Logger


class Version:
    """Represents a version number, like "3.2.8" and allows comparison of those
    numbers.
    """

    def __init__(self, version: Union[str, bytes, int, "Version", List[Union[int, str, bytes]]]) -> None:
        """Constructs the version instance from a string representing the version.

        The string representation may have dashes or underscores that separate
        the major, minor and revision version numbers. All text is ignored.

        :param version: A string or bytes representing a version number.
        """

        super().__init__()

        if type(version) == bytes:
            version = cast(bytes, version)
            version = version.decode("utf-8")

        if isinstance(version, str):
            version = cast(str, version)
            # Versions are in (MOD-)x.x.x(-POSTFIX.x) format.
            version = version.replace("MOD-", "")
            version = version.replace("-", ".")
            version = version.replace("_", ".")
            version = version.replace("\"", "")
            version = re.sub(r"[A-Z]+", "", version)
            version_list = version.split(".")  # type: ignore
        elif isinstance(version, list):
            version_list = version  # type: ignore
        elif isinstance(version, int):
            version_list = [version]  # type: ignore
        elif isinstance(version, Version):
            version_list = [version.getMajor(), version.getMinor(), version.getRevision(), version.getPostfixType(), version.getPostfixVersion()]  # type: ignore
        else:
            Logger.log("w", "Unable to convert version %s of type %s into a usable version", version, type(version))
            version_list = []

        self._major = 0
        self._minor = 0
        self._revision = 0
        self._postfix_type = ""
        self._postfix_version = 0
        try:
            self._major = int(version_list[0])
            self._minor = int(version_list[1])
            self._revision = int(version_list[2])
            self._postfix_type = version_list[3]
            self._postfix_version = int(version_list[4])
        except IndexError:
            pass
        except ValueError:
            pass

    def getMajor(self) -> int:
        """Gets the major version number.

        The major version number is the first number of the version: "3" in the
        version "3.2.8".
        """

        return self._major

    def getMinor(self) -> int:
        """Gets the minor version number.

        The minor version number is the second number of the version: "2" in the
        version "3.2.8".
        """

        return self._minor

    def getRevision(self) -> int:
        """Gets the revision or patch version number.

        The revision version number is the third number of the version: "8" in
        the version "3.2.8".
        """

        return self._revision

    def getPostfixType(self) -> str:
        """Gets the postfix type.

        The postfix type is the name of the postfix, e.g. "alpha" in the version "1.2.3-alpha.4"
        """

        return self._postfix_type

    def getPostfixVersion(self) -> int:
        """Gets the postfix version number.

        The postfix version is the last number, e.g. "4" in the version "1.2.3-alpha.4"
        """

        return self._postfix_version

    def hasPostFix(self) -> bool:
        """Check if a version has a postfix."""

        return self.getPostfixVersion() > 0 and self._postfix_type != ""

    def __gt__(self, other: Union["Version", str]) -> bool:
        """Indicates whether this version is later than the specified version.

        Implements the > operator.

        :param other: Either another version object or a string representing one.
        """

        if isinstance(other, Version):
            return other.__lt__(self)
        elif isinstance(other, str):
            return Version(other).__lt__(self)
        else:
            return False

    def __lt__(self, other: Union["Version", str]) -> bool:
        """Indicates whether this version is earlier than the specified version.

        Implements the < operator.

        :param other: Either another version object or a string representing one.
        """

        if isinstance(other, Version):
            if self._major < other.getMajor():
                # The major version is lower.
                return True
            if self._minor < other.getMinor() \
                    and self._major == other.getMajor():
                # The minor version is lower.
                return True
            if self._revision < other.getRevision() \
                    and self._major == other.getMajor() \
                    and self._minor == other.getMinor():
                # The revision version is lower.
                return True
            if self.hasPostFix() and other.hasPostFix() \
                    and self._postfix_version < other.getPostfixVersion() \
                    and self._postfix_type == other.getPostfixType() \
                    and self._revision == other.getRevision() \
                    and self._major == other.getMajor() \
                    and self._minor == other.getMinor():
                # The postfix version is lower. This is only allowed if the postfix type is the same!
                return True
            if self.hasPostFix() and not other.hasPostFix():
                # If the root version is the same but the other has no postfix, we consider the other larger.
                # E.g. Version("1.0.0") > Version("1.0.0-alpha.7")
                return Version("{}.{}.{}".format(
                    self.getMajor(),
                    self.getMinor(),
                    self.getRevision()
                )) == other
            return False
        elif isinstance(other, str):
            return self < Version(other)
        else:
            return False

    def __eq__(self, other: object) -> bool:
        """Indicates whether this version is equal to the specified version.

        Implements the == operator.

        :param other: Either another version object or a string representing one.
        """

        if isinstance(other, Version):
            # Direct comparison with same type.
            return self._major == other.getMajor() \
                   and self._minor == other.getMinor() \
                   and self._revision == other.getRevision() \
                   and self._postfix_type == other.getPostfixType() \
                   and self._postfix_version == other.getPostfixVersion()

        if isinstance(other, str):
            # Comparison with string by converting to Version first.
            return self == Version(other)

        return False

    def __ge__(self, other: Union["Version", str]) -> bool:
        """Indicates whether this version is later or equal to the specified
        version.

        Implements the >= operator.

        :param other: Either another version object or a string representing one.
        """

        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other: Union["Version", str]) -> bool:
        """Indicates whether this version is earlier or equal to the specified
        version.

        Implements the <= operator.

        :param other: Either another version object or a string representing one.
        """

        return self.__lt__(other) or self.__eq__(other)

    def __str__(self) -> str:
        """Returns a string representation containing the major, minor and revision
        number.

        Such as "3.2.8".
        """

        if self._postfix_type:
            # If we have a postfix, return a string including that postfix.
            return "%s.%s.%s-%s.%s"\
                   % (self._major, self._minor, self._revision, self._postfix_type, self._postfix_version)
        return "%s.%s.%s" % (self._major, self._minor, self._revision)

    def __hash__(self) -> int:
        """Returns a number reasonably representing the identity of the version."""

        return hash(self.__str__())
