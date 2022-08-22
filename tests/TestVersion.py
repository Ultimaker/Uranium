# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Version import Version
from unittest import TestCase
import pytest

major_versions = [Version("1"), Version(b"1"), Version(1), Version([1]), Version(["1"]), Version("1."), Version("MOD-1"), Version("1B"), Version(Version("1"))]
major_minor_versions = [Version("1.2"), Version("1-2"), Version("1_2"), Version(b"1.2"), Version("1.2BETA"), Version([1, 2]), Version(["1", "2"]), Version([1, "2"]), Version([1, b"2"])]
major_minor_revision_versions = [Version("1.2.3"), Version("1.2.3BETA"), Version("1_2-3"), Version(b"1.2.3"), Version([1, 2, 3]), Version(["1", "2", "3"]), Version([1, "2", 3]), Version("MOD-1.2.3"), Version(["1", 2, b"3"])]


def check_version_equals(first_version: Version, second_version: Version):
    assert first_version == second_version
    assert first_version.getMajor() == second_version.getMajor()
    assert first_version.getMinor() == second_version.getMinor()
    assert first_version.getRevision() == second_version.getRevision()


@pytest.mark.parametrize("first_version", major_versions)
@pytest.mark.parametrize("second_version", major_versions)
def test_major_equals(first_version, second_version):
    check_version_equals(first_version, second_version)


@pytest.mark.parametrize("first_version", major_minor_versions)
@pytest.mark.parametrize("second_version", major_minor_versions)
def test_major_and_minor_equals(first_version, second_version):
    check_version_equals(first_version, second_version)


@pytest.mark.parametrize("first_version", major_minor_revision_versions)
@pytest.mark.parametrize("second_version", major_minor_revision_versions)
def test_major_minor_revision_equals(first_version, second_version):
    check_version_equals(first_version, second_version)


@pytest.mark.parametrize("first_version", major_versions)
@pytest.mark.parametrize("second_version", major_minor_versions)
def test_check_version_smaller(first_version, second_version):
    assert first_version < second_version

    # Just to be on the really safe side
    assert first_version != second_version
    assert not first_version > second_version


@pytest.mark.parametrize("first_version", major_minor_versions)
@pytest.mark.parametrize("second_version", major_minor_revision_versions)
def test_check_version_smaller_2(first_version, second_version):
    assert first_version < second_version

    # Just to be on the really safe side
    assert first_version != second_version
    assert not first_version > second_version


def test_versionPostfix():
    version = Version("1.2.3-alpha.4")
    assert version.getPostfixType() == "alpha"
    assert version.getPostfixVersion() == 4
    assert version.hasPostFix()
    assert not Version("").hasPostFix()

    assert version <= Version("1.2.3-alpha.5")
    assert version < Version("1.2.3-alpha.5")

def test_postfix_format():
    beta_1 = Version([1, 2, 3, "beta", 1])
    beta_2 = Version([1, 2, 3, "beta", 2])
    assert beta_2 > beta_1
    assert beta_2 != beta_1

def test_old_beta():
    release = Version([5, 1, 0])
    beta = Version([5, 1, 0, "beta", 2])
    assert release > beta

def test_new_beta():
    release_old = Version([5, 1, 0])
    beta_new = Version([5, 2, 0, "beta", 2])
    assert release_old < beta_new

def test_missing_prerelease_number():
    beta_missing_version_number = Version("1.2.3-beta.")
    beta_version_number = Version("1.2.3-beta.1")
    assert beta_version_number > beta_missing_version_number

def test_ignores_build_metadata():
    beta_old_metadata = Version("1.2.3-beta.1+500")
    beta_new_metadata = Version("1.2.3-beta.2+50")
    assert beta_new_metadata > beta_old_metadata

def test_versionWeirdCompares():
    version = Version("1.2.3-alpha.4")
    assert not version == 12


def test_wrongType():
    version = Version(None)
    assert version == Version("0")


def test_compareStrings():
    version_string = "1.0.0"
    version = Version(version_string)
    assert version == version_string
    assert version >= version_string

    assert version < "2.0.0"
    assert version <= "2.0.0"
    assert "0" < version

    assert Version("1.0.0") > Version("1.0.0-alpha.7")

    # Defend people from ignoring the typing.
    assert not version > None
    assert not version < None


def test_compareBeta():
    normal_version = Version("1.0.0")
    beta_version = Version("1.0.0-BETA")
    assert normal_version > beta_version


def test_comparePostfixVersion():
    assert Version("1.0.0-alpha.1") < Version("1.0.0-alpha.2")