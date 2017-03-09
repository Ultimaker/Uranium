# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import re #To replace parts of version strings with regex.

class Version(object):
    def __init__(self, version):
        super().__init__()
        if isinstance(version, str):
            version = version.replace("-", ".")
            version = version.replace("_", ".")
            version = re.sub(r"[A-Z]+", ".", version)
            version_list = version.split(".")
        else:
            version_list = version
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

    def getMajor(self):
        return self._major

    def getMinor(self):
        return self._minor

    def getRevision(self):
        return self._revision

    def __gt__(self, other):
        if isinstance(other, Version):
            return other.__lt__(self)
        elif isinstance(other, str):
            return Version(other).__lt__(self)
        else:
            return False

    def __lt__(self, other):
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

    def __eq__(self, other):
        if isinstance(other, Version):
            return self._major == other.getMajor() and self._minor == other.getMinor() and self._revision == other.getRevision()
        elif isinstance(other, str):
            return self == Version(other)
        else:
            return False

    def __str__(self):
        return "%s.%s.%s" %(self._major, self._minor, self._revision)

    def __hash__(self):
        return hash(self.__str__())
