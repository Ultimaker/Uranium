# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Version import Version
from unittest import TestCase


class TestResources(TestCase):
    def test_version(self):
        self.assertTrue(Version("1.1.0") > Version("1.0.0"))
        self.assertTrue(Version("2.1.0") > Version("1.5.0"))
        self.assertTrue(Version("2.1.0") > Version("1.1.0"))
        self.assertTrue(Version("1.1.2") > Version("1.1.1"))
        self.assertTrue(Version("1.1.2") == Version("1.1.2"))

    def test_version2(self):
        self.assertTrue(Version("1.1.0-alpha.2") > Version("1.1.0-alpha.1"))
        self.assertTrue(Version("1.1.0-alpha.2") == Version("1.1.0-alpha.2"))
        self.assertFalse(Version("1.1.0-alpha.2") > Version("1.1.1-alpha.1"))
        self.assertTrue(Version("2.1.0-beta") > Version("1.5.0"))
        self.assertFalse(Version("1.1.2-beta.2") > Version("1.1.2.alpha.1"))
        self.assertTrue(Version("1.0.0") > Version("1.0.0-alpha.7"))

    def test_malformed_versions(self):
        v1 = Version("This is a strange version number")
        v2 = Version("2.3.4.5-beta.2.3")
        v1 > v2  # Just don't crash

    def test_other_comparisons(self):
        self.assertFalse(Version("1.1.0-beta.2") == Version("1.1.0-alpha.2"))
        self.assertFalse(Version("1.1.0-beta.2") > Version("1.1.0-alpha.2"))
        self.assertFalse(Version("1.1.0-beta.2") < Version("1.1.0-alpha.2"))
