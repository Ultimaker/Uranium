# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

import os

import pytest

from UM.Resources import Resources, ResourcePackage
from UM.SemanticVersion import SemanticVersion


@pytest.fixture(autouse = True)
def restore_resources_state():
    paths = list(Resources._Resources__paths)
    packages = dict(Resources._Resources__packages)
    yield
    Resources._Resources__paths[:] = paths
    Resources._Resources__packages.clear()
    Resources._Resources__packages.update(packages)


def test_registerAddsSearchPathAndKeepsInfo(tmp_path):
    Resources.registerPackageSearchPath(str(tmp_path), "my_printer", SemanticVersion("1.2.3"), is_bundled = True)

    assert str(tmp_path) in Resources._Resources__paths
    package = Resources.getPackageForPath(str(tmp_path / "definitions" / "printer.def.json"))
    assert package == ResourcePackage("my_printer", SemanticVersion("1.2.3"), True, str(tmp_path))


def test_packageOfPathOutsideAnyPackageIsNone(tmp_path):
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    Resources.registerPackageSearchPath(str(package_dir), "my_printer", SemanticVersion("1.0.0"))

    assert Resources.getPackageForPath(str(tmp_path / "other" / "file.def.json")) is None
    assert Resources.getPackageForPath(str(tmp_path / "package_sibling" / "file.def.json")) is None  # Not a path prefix match.


def test_nestedPackageRootsUseTheClosestRoot(tmp_path):
    outer = tmp_path / "outer"
    inner = outer / "inner"
    inner.mkdir(parents = True)
    Resources.registerPackageSearchPath(str(outer), "outer", SemanticVersion("1.0.0"))
    Resources.registerPackageSearchPath(str(inner), "inner", SemanticVersion("2.0.0"))

    assert Resources.getPackageForPath(str(inner / "a.def.json")).package_id == "inner"
    assert Resources.getPackageForPath(str(outer / "a.def.json")).package_id == "outer"


def test_removeSearchPathForgetsPackage(tmp_path):
    Resources.registerPackageSearchPath(str(tmp_path), "my_printer", SemanticVersion("1.0.0"))
    Resources.removeSearchPath(str(tmp_path))

    assert Resources.getPackageForPath(str(tmp_path / "a.def.json")) is None


def test_registerNonExistingPathIsIgnored(tmp_path):
    missing = tmp_path / "missing"
    Resources.registerPackageSearchPath(str(missing), "my_printer", SemanticVersion("1.0.0"))

    assert Resources.getPackageForPath(str(missing / "a.def.json")) is None


def test_registerRequiresSemanticVersion(tmp_path):
    with pytest.raises(TypeError):
        Resources.registerPackageSearchPath(str(tmp_path), "my_printer", "1.0.0")  # type: ignore


def test_pathComparisonIsNormalised(tmp_path):
    Resources.registerPackageSearchPath(str(tmp_path), "my_printer", SemanticVersion("1.0.0"))
    unnormalised = os.path.join(str(tmp_path), "sub", "..", "definitions", "a.def.json")

    assert Resources.getPackageForPath(unnormalised) is not None


def test_getSearchPathForFile(tmp_path):
    outer = tmp_path / "outer"
    inner = outer / "inner"
    inner.mkdir(parents = True)
    Resources.addSearchPath(str(outer))
    Resources.addSearchPath(str(inner))

    assert Resources.getSearchPathForFile(str(inner / "definitions" / "a.def.json")) == str(inner)
    assert Resources.getSearchPathForFile(str(outer / "definitions" / "a.def.json")) == str(outer)
    assert Resources.getSearchPathForFile(str(tmp_path / "elsewhere" / "a.def.json")) is None
    assert Resources.getSearchPathForFile(str(tmp_path / "outer_sibling" / "a.def.json")) is None
