# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest

from UM.SemanticVersion import SemanticVersion


def test_parseComponents():
    version = SemanticVersion("1.2.3-alpha.4+build.5")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == ("alpha", 4)
    assert version.build == ("build", "5")
    assert str(version) == "1.2.3-alpha.4+build.5"


def test_parsePlain():
    version = SemanticVersion("10.0.7")
    assert (version.major, version.minor, version.patch) == (10, 0, 7)
    assert version.prerelease == ()
    assert version.build == ()
    assert not version.isPrerelease()
    assert str(version) == "10.0.7"


@pytest.mark.parametrize("malformed", [
    "", "1", "1.2", "1.2.3.4", "01.2.3", "1.02.3", "1.2.03", "1.2.3-", "1.2.3-01", "1.2.3-a..b", "1.2.3+",
    "1.2.3+a..b", "v1.2.3", " 1.2.3", "1.2.3 ", "1.2.-3", "a.b.c", "1.2.3-a_b", "MOD-1.2.3", "1.2.3_beta",
])
def test_malformedRaises(malformed):
    with pytest.raises(ValueError):
        SemanticVersion(malformed)


@pytest.mark.parametrize("not_a_string", [None, 1, 1.2, b"1.2.3", [1, 2, 3]])
def test_nonStringRaises(not_a_string):
    with pytest.raises(ValueError):
        SemanticVersion(not_a_string)


def test_tryParse():
    assert SemanticVersion.tryParse("1.2.3") == SemanticVersion("1.2.3")
    assert SemanticVersion.tryParse("garbage") is None
    assert SemanticVersion.tryParse(None) is None


def test_precedenceFromSpecification():
    # The ordering example from https://semver.org/#spec-item-11
    ordered = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11",
               "1.0.0-rc.1", "1.0.0", "2.0.0", "2.1.0", "2.1.1"]
    versions = [SemanticVersion(v) for v in ordered]
    for index, lower in enumerate(versions):
        for higher in versions[index + 1:]:
            assert lower < higher
            assert higher > lower
            assert lower <= higher
            assert higher >= lower
            assert lower != higher
            assert not lower > higher
            assert not higher < lower


def test_numericComparedNumerically():
    assert SemanticVersion("1.9.0") < SemanticVersion("1.10.0")
    assert SemanticVersion("1.0.0-2") < SemanticVersion("1.0.0-10")
    assert SemanticVersion("1.0.0-9") < SemanticVersion("1.0.0-a")  # Numeric identifiers rank below alphanumeric.


def test_buildMetadataIgnoredForPrecedence():
    first = SemanticVersion("1.2.3+500")
    second = SemanticVersion("1.2.3+50")
    assert first == second
    assert not first < second
    assert not first > second
    assert hash(first) == hash(second)
    assert SemanticVersion("1.2.3-beta.1+a") == SemanticVersion("1.2.3-beta.1+b")


def test_sortable():
    shuffled = [SemanticVersion(v) for v in ["1.10.0", "1.2.0", "1.2.0-rc.1", "0.9.9"]]
    assert [str(v) for v in sorted(shuffled)] == ["0.9.9", "1.2.0-rc.1", "1.2.0", "1.10.0"]
    assert str(max(shuffled)) == "1.10.0"


def test_compareWithString():
    version = SemanticVersion("1.2.3")
    assert version == "1.2.3"
    assert version < "1.2.4"
    assert version >= "1.2.3"
    assert "1.2.2" < version


def test_compareWithInvalidOrOtherTypes():
    version = SemanticVersion("1.2.3")
    assert version != "garbage"
    assert version != 1
    assert version != None  # noqa: E711
    with pytest.raises(TypeError):
        version < "garbage"
    with pytest.raises(TypeError):
        version > None


def test_hashUsableInSets():
    assert len({SemanticVersion("1.0.0"), SemanticVersion("1.0.0+meta"), SemanticVersion("1.0.1")}) == 2


def test_isPrerelease():
    assert SemanticVersion("1.0.0-rc.1").isPrerelease()
    assert not SemanticVersion("1.0.0+rc").isPrerelease()
