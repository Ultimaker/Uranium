# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

import re
from functools import total_ordering
from typing import Any, Optional, Tuple, Union

# Grammar and precedence rules from https://semver.org/spec/v2.0.0.html
_NUMERIC_IDENTIFIER = r"(?:0|[1-9][0-9]*)"
_PRERELEASE_IDENTIFIER = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
_BUILD_IDENTIFIER = r"[0-9A-Za-z-]+"
_SEMVER_REGEX = re.compile(
    rf"^(?P<major>{_NUMERIC_IDENTIFIER})\.(?P<minor>{_NUMERIC_IDENTIFIER})\.(?P<patch>{_NUMERIC_IDENTIFIER})"
    rf"(?:-(?P<prerelease>{_PRERELEASE_IDENTIFIER}(?:\.{_PRERELEASE_IDENTIFIER})*))?"
    rf"(?:\+(?P<build>{_BUILD_IDENTIFIER}(?:\.{_BUILD_IDENTIFIER})*))?$"
)

Identifier = Union[int, str]


@total_ordering
class SemanticVersion:
    """A strictly parsed Semantic Version 2.0.0, with spec-compliant precedence.

    Unlike :class:`UM.Version.Version`, which leniently accepts many formats, this class rejects anything that is
    not a valid semantic version by raising a ValueError. Build metadata is kept, but it is ignored when comparing.
    Instances are immutable.
    """

    __slots__ = ("_major", "_minor", "_patch", "_prerelease", "_build")

    def __init__(self, version: str) -> None:
        """Parses a semantic version string such as "1.2.3", "1.2.3-rc.1" or "1.2.3-rc.1+build.5".

        :param version: The version string. Must be a str without surrounding whitespace or a leading "v".
        :raises ValueError: If the version is not a valid semantic version.
        """

        if not isinstance(version, str):
            raise ValueError(f"A semantic version must be a string, got {type(version).__name__}.")
        match = _SEMVER_REGEX.match(version)
        if match is None or version.endswith("\n"):  # "$" would otherwise accept a trailing newline.
            raise ValueError(f"'{version}' is not a valid semantic version.")

        self._major = int(match.group("major"))
        self._minor = int(match.group("minor"))
        self._patch = int(match.group("patch"))
        prerelease = match.group("prerelease")
        self._prerelease = tuple(self._toIdentifier(part) for part in prerelease.split(".")) if prerelease else ()
        build = match.group("build")
        self._build = tuple(build.split(".")) if build else ()

    @staticmethod
    def _toIdentifier(part: str) -> Identifier:
        return int(part) if part.isdigit() else part

    @classmethod
    def tryParse(cls, version: Any) -> Optional["SemanticVersion"]:
        """Parses a version, returning None instead of raising when it is not valid."""

        try:
            return cls(version)
        except ValueError:
            return None

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    @property
    def patch(self) -> int:
        return self._patch

    @property
    def prerelease(self) -> Tuple[Identifier, ...]:
        """The dot-separated pre-release identifiers; numeric identifiers are integers."""

        return self._prerelease

    @property
    def build(self) -> Tuple[str, ...]:
        """The dot-separated build metadata identifiers. These do not take part in comparisons."""

        return self._build

    def isPrerelease(self) -> bool:
        return len(self._prerelease) > 0

    def _precedenceKey(self) -> Tuple[Any, ...]:
        # A version without pre-release ranks above the same version with one. Within the pre-release identifiers,
        # numeric ones rank below alphanumeric ones, and a shorter list ranks below a longer one with the same prefix
        # (tuple comparison already does the latter).
        prerelease_key = tuple((0, part, "") if isinstance(part, int) else (1, 0, part) for part in self._prerelease)
        return self._major, self._minor, self._patch, 0 if self._prerelease else 1, prerelease_key

    @staticmethod
    def _coerce(other: Any) -> Optional["SemanticVersion"]:
        if isinstance(other, SemanticVersion):
            return other
        if isinstance(other, str):
            return SemanticVersion.tryParse(other)
        return None

    def __eq__(self, other: object) -> bool:
        other_version = self._coerce(other)
        if other_version is None:
            return False
        return self._precedenceKey() == other_version._precedenceKey()

    def __lt__(self, other: Any) -> bool:
        other_version = self._coerce(other)
        if other_version is None:
            raise TypeError(f"Cannot compare a SemanticVersion with {other!r}.")
        return self._precedenceKey() < other_version._precedenceKey()

    def __hash__(self) -> int:
        return hash(self._precedenceKey())

    def __str__(self) -> str:
        result = f"{self._major}.{self._minor}.{self._patch}"
        if self._prerelease:
            result += "-" + ".".join(str(part) for part in self._prerelease)
        if self._build:
            result += "+" + ".".join(self._build)
        return result

    def __repr__(self) -> str:
        return f"SemanticVersion('{self}')"
