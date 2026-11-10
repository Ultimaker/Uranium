# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

import importlib.util
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from UM.MimeTypeDatabase import MimeType
from UM.Resources import Resources
from UM.SemanticVersion import SemanticVersion
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Version import Version

DEFINITION_MIME = MimeType(name = "application/x-uranium-test-definition", comment = "Test definition", suffixes = ["def.json"])
MATERIAL_MIME = MimeType(name = "application/x-uranium-test-material", comment = "Test material", suffixes = ["fdm_material"])

PROVIDER_PATH = os.path.join(os.path.dirname(__file__), "..", "plugins", "LocalContainerProvider", "LocalContainerProvider.py")


@pytest.fixture(scope = "module")
def provider_class():
    spec = importlib.util.spec_from_file_location("LocalContainerProviderUnderTest", PROVIDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LocalContainerProvider


@pytest.fixture(autouse = True)
def restore_state():
    paths = list(Resources._Resources__paths)
    packages = dict(Resources._Resources__packages)
    independent = set(ContainerRegistry.independently_versioned_mime_types)
    ContainerRegistry.independently_versioned_mime_types.add(MATERIAL_MIME.name)
    yield
    Resources._Resources__paths[:] = paths
    Resources._Resources__packages.clear()
    Resources._Resources__packages.update(packages)
    ContainerRegistry.independently_versioned_mime_types.clear()
    ContainerRegistry.independently_versioned_mime_types.update(independent)


def makePackage(tmp_path, name, version, is_bundled):
    root = tmp_path / name
    (root / "definitions").mkdir(parents = True)
    if version is not None:
        Resources.registerPackageSearchPath(str(root), name, SemanticVersion(version), is_bundled)
    return root


def select(provider_class, candidates, container_versions = None, mime = DEFINITION_MIME):
    """Runs the selection. The candidates are paths in priority order; the version of a container is looked up by path."""
    container_versions = container_versions or {}
    provider = provider_class()
    container_id = os.path.basename(str(candidates[0])).split(".")[0]  # The candidates are files that all provide the same container.
    with patch.object(provider_class, "_getContainerVersion", side_effect = lambda _id, path, _mime: Version(container_versions.get(path, "0"))):
        path, _ = provider._selectNewestCandidate(container_id, [(str(p), mime) for p in candidates])
    return path


def test_higherPackageVersionWins(provider_class, tmp_path):
    bundled = makePackage(tmp_path, "bundled", "1.0.0", True) / "definitions" / "printer.def.json"
    installed = makePackage(tmp_path, "installed", "1.1.0", False) / "definitions" / "printer.def.json"

    assert select(provider_class, [bundled, installed]) == str(installed)
    assert select(provider_class, [installed, bundled]) == str(installed)


def test_bundledWinsWhenNewerThanInstalled(provider_class, tmp_path):
    bundled = makePackage(tmp_path, "bundled", "2.0.0", True) / "definitions" / "printer.def.json"
    installed = makePackage(tmp_path, "installed", "1.9.9", False) / "definitions" / "printer.def.json"

    assert select(provider_class, [installed, bundled]) == str(bundled)
    assert select(provider_class, [bundled, installed]) == str(bundled)


def test_prereleaseIsLowerThanRelease(provider_class, tmp_path):
    bundled = makePackage(tmp_path, "bundled", "1.0.0", True) / "definitions" / "printer.def.json"
    installed = makePackage(tmp_path, "installed", "1.0.0-rc.1", False) / "definitions" / "printer.def.json"

    assert select(provider_class, [installed, bundled]) == str(bundled)


@pytest.mark.parametrize("bundled_first", [True, False])
def test_equalPackageVersionPrefersInstalled(provider_class, tmp_path, bundled_first):
    bundled = makePackage(tmp_path, "bundled", "1.0.0", True) / "definitions" / "printer.def.json"
    installed = makePackage(tmp_path, "installed", "1.0.0+other.build", False) / "definitions" / "printer.def.json"

    candidates = [bundled, installed] if bundled_first else [installed, bundled]
    assert select(provider_class, candidates) == str(installed)


def test_fileOutsidePackagesCountsAsVersionZeroAndBundled(provider_class, tmp_path):
    plain = tmp_path / "resources" / "definitions" / "printer.def.json"
    installed_zero = makePackage(tmp_path, "installed", "0.0.0", False) / "definitions" / "printer.def.json"
    installed_one = makePackage(tmp_path, "installed_one", "0.0.1", False) / "definitions" / "printer.def.json"

    assert select(provider_class, [plain, installed_zero]) == str(installed_zero)
    assert select(provider_class, [plain, installed_one]) == str(installed_one)


def test_noPackagesKeepsContainerVersionThenPriority(provider_class, tmp_path):
    first = tmp_path / "first" / "printer.def.json"
    second = tmp_path / "second" / "printer.def.json"

    assert select(provider_class, [first, second]) == str(first)
    assert select(provider_class, [first, second], {str(second): "3"}) == str(second)
    assert select(provider_class, [first, second], {str(first): "3", str(second): "3"}) == str(first)


def test_containerVersionBreaksTieBetweenPackageVersions(provider_class, tmp_path):
    first = makePackage(tmp_path, "first", "1.0.0", False) / "definitions" / "printer.def.json"
    second = makePackage(tmp_path, "second", "1.0.0", False) / "definitions" / "printer.def.json"

    assert select(provider_class, [first, second], {str(second): "5"}) == str(second)


def test_packageVersionOutranksContainerVersion(provider_class, tmp_path):
    older = makePackage(tmp_path, "older", "1.0.0", False) / "definitions" / "printer.def.json"
    newer = makePackage(tmp_path, "newer", "1.0.1", True) / "definitions" / "printer.def.json"

    assert select(provider_class, [older, newer], {str(older): "9"}) == str(newer)


def test_materialsIgnorePackageVersions(provider_class, tmp_path):
    bundled = makePackage(tmp_path, "bundled", "1.0.0", True) / "definitions" / "m.xml.fdm_material"
    installed = makePackage(tmp_path, "installed", "9.0.0", False) / "definitions" / "m.xml.fdm_material"

    # Without versions, the first in priority order wins, even though the second belongs to a much newer package.
    assert select(provider_class, [bundled, installed], mime = MATERIAL_MIME) == str(bundled)
    # The version of the material itself decides.
    assert select(provider_class, [bundled, installed], {str(installed): "2"}, mime = MATERIAL_MIME) == str(installed)
    assert select(provider_class, [bundled, installed], {str(bundled): "2"}, mime = MATERIAL_MIME) == str(bundled)


def test_singleCandidateIsReturned(provider_class, tmp_path):
    only = makePackage(tmp_path, "only", "1.0.0", False) / "definitions" / "printer.def.json"

    assert select(provider_class, [only]) == str(only)


def makeCachedDefinition(own_path, inherited_paths):
    definition = MagicMock()
    definition.getPath.return_value = str(own_path)
    definition.getInheritedFiles.return_value = [str(path) for path in inherited_paths]
    return definition


def providerWithSelectedFiles(provider_class, id_to_path):
    """A provider that uses the given files, as it would after looking for the containers."""
    provider = provider_class()
    provider._id_to_path = {container_id: str(path) for container_id, path in id_to_path.items()}
    provider._selected_paths = {provider._normalizePath(path) for path in provider._id_to_path.values()}
    return provider


def test_cacheIsCurrentWhenMadeFromTheFilesInUse(provider_class, tmp_path):
    provider = providerWithSelectedFiles(provider_class, {"base": tmp_path / "a" / "base.def.json", "child": tmp_path / "a" / "child.def.json"})
    definition = makeCachedDefinition(tmp_path / "a" / "child.def.json", [tmp_path / "a" / "base.def.json"])

    assert provider._isCacheFromCurrentFiles(definition)


def test_cacheIsStaleWhenParentChoiceChanged(provider_class, tmp_path):
    provider = providerWithSelectedFiles(provider_class, {"base": tmp_path / "b" / "base.def.json", "child": tmp_path / "a" / "child.def.json"})
    definition = makeCachedDefinition(tmp_path / "a" / "child.def.json", [tmp_path / "a" / "base.def.json"])

    assert not provider._isCacheFromCurrentFiles(definition)


def test_cacheIsStaleWhenOwnFileChoiceChanged(provider_class, tmp_path):
    provider = providerWithSelectedFiles(provider_class, {"child": tmp_path / "b" / "child.def.json"})
    definition = makeCachedDefinition(tmp_path / "a" / "child.def.json", [])

    assert not provider._isCacheFromCurrentFiles(definition)


def test_cacheIsStaleWhenTheFileWasProvidedByAnotherLocationBefore(provider_class, tmp_path):
    # E.g. the package that provided the cached files was uninstalled, so the bundled files are used now. Nothing
    # conflicts anymore, but the cache was made from other files.
    provider = providerWithSelectedFiles(provider_class, {"base": tmp_path / "bundled" / "base.def.json", "child": tmp_path / "bundled" / "child.def.json"})

    assert not provider._isCacheFromCurrentFiles(makeCachedDefinition(tmp_path / "plugin" / "child.def.json", [tmp_path / "plugin" / "base.def.json"]))
    assert not provider._isCacheFromCurrentFiles(makeCachedDefinition(tmp_path / "bundled" / "child.def.json", [tmp_path / "plugin" / "base.def.json"]))
    assert provider._isCacheFromCurrentFiles(makeCachedDefinition(tmp_path / "bundled" / "child.def.json", [tmp_path / "bundled" / "base.def.json"]))


def test_cacheComparesPathsIndependentOfTheirNotation(provider_class, tmp_path):
    provider = providerWithSelectedFiles(provider_class, {"base": tmp_path / "a" / "base.def.json"})
    definition = makeCachedDefinition(tmp_path / "a" / "sub" / ".." / "base.def.json", [])

    assert provider._isCacheFromCurrentFiles(definition)


REAL_DEFINITION_MIME = MimeType(name = "application/x-uranium-definitioncontainer", comment = "Definition", suffixes = ["def.json"])
REAL_INSTANCE_MIME = MimeType(name = "application/x-uranium-instancecontainer", comment = "Instance", suffixes = ["inst.cfg"])


def writeBundledDefinition(root, definition_id, version = None, extra_metadata = None, inherits = None):
    """Writes a definition in a plain search path, like the resources that ship with the application."""
    metadata = dict(extra_metadata or {})
    if version is not None:
        metadata["package_version"] = version
    data = {"version": 2, "name": definition_id, "metadata": metadata, "settings": {}}
    if inherits:
        data["inherits"] = inherits
    (root / "definitions").mkdir(parents = True, exist_ok = True)
    path = root / "definitions" / f"{definition_id}.def.json"
    path.write_text(json.dumps(data), encoding = "utf-8")
    return path


def writeBundledProfile(root, folder, container_id, definition_id, version = None):
    (root / folder).mkdir(parents = True, exist_ok = True)
    path = root / folder / f"{container_id}.inst.cfg"
    path.write_text(f"[general]\nversion = 4\nname = Profile\ndefinition = {definition_id}\n\n[metadata]\ntype = quality\nsetting_version = 27\n" + (f"package_version = {version}\n" if version is not None else ""), encoding = "utf-8")
    return path


@pytest.fixture
def bundled_root(tmp_path):
    root = tmp_path / "bundled_resources"
    root.mkdir()
    Resources.addSearchPath(str(root))
    return root


def installedDefinition(tmp_path, name, version, definition_id = "printer"):
    root = makePackage(tmp_path, name, version, False)
    return root / "definitions" / f"{definition_id}.def.json"


def test_bundledPrinterVersionComesFromItsDefinition(provider_class, tmp_path, bundled_root):
    bundled = writeBundledDefinition(bundled_root, "printer", "1.1.0")
    installed = installedDefinition(tmp_path, "installed", "1.0.0")

    assert select(provider_class, [installed, bundled], mime = REAL_DEFINITION_MIME) == str(bundled)
    assert select(provider_class, [bundled, installed], mime = REAL_DEFINITION_MIME) == str(bundled)


def test_onlyTheUpdatedBundledPrinterWinsOverItsInstalledPackage(provider_class, tmp_path, bundled_root):
    updated = writeBundledDefinition(bundled_root, "printer_a", "1.1.0")
    unchanged = writeBundledDefinition(bundled_root, "printer_b", "1.0.0")
    behind = writeBundledDefinition(bundled_root, "printer_c", "1.0.0")
    installed_a = installedDefinition(tmp_path, "installed_a", "1.0.0", "printer_a")
    installed_b = installedDefinition(tmp_path, "installed_b", "1.0.0", "printer_b")
    installed_c = installedDefinition(tmp_path, "installed_c", "1.2.0", "printer_c")

    assert select(provider_class, [installed_a, updated], mime = REAL_DEFINITION_MIME) == str(updated)
    assert select(provider_class, [unchanged, installed_b], mime = REAL_DEFINITION_MIME) == str(installed_b)  # Tie: installed wins.
    assert select(provider_class, [behind, installed_c], mime = REAL_DEFINITION_MIME) == str(installed_c)


def test_bundledExtruderUsesTheVersionOfItsMachine(provider_class, tmp_path, bundled_root):
    writeBundledDefinition(bundled_root, "printer", "1.1.0")
    extruders = bundled_root / "extruders"
    extruders.mkdir()
    bundled = extruders / "printer_extruder_0.def.json"
    bundled.write_text(json.dumps({"version": 2, "name": "Extruder", "metadata": {"machine": "printer"}, "settings": {}}), encoding = "utf-8")
    installed = installedDefinition(tmp_path, "installed", "1.0.0", "printer_extruder_0")

    assert select(provider_class, [installed, bundled], mime = REAL_DEFINITION_MIME) == str(bundled)


def test_bundledProfileUsesTheVersionOfItsDefinition(provider_class, tmp_path, bundled_root, upgrade_manager):
    writeBundledDefinition(bundled_root, "printer", "1.1.0")
    bundled = writeBundledProfile(bundled_root, "quality", "printer_fine", "printer")
    installed_root = makePackage(tmp_path, "installed", "1.0.0", False)
    installed = writeBundledProfile(installed_root, "quality", "printer_fine", "printer")

    assert select(provider_class, [installed, bundled], mime = REAL_INSTANCE_MIME) == str(bundled)
    assert select(provider_class, [bundled, installed], mime = REAL_INSTANCE_MIME) == str(bundled)


def test_definitionWithoutOwnVersionUsesItsParent(provider_class, tmp_path, bundled_root):
    writeBundledDefinition(bundled_root, "base", "1.1.0")
    bundled = writeBundledDefinition(bundled_root, "printer", None, inherits = "base")
    installed = installedDefinition(tmp_path, "installed", "1.0.0")

    assert select(provider_class, [installed, bundled], mime = REAL_DEFINITION_MIME) == str(bundled)


@pytest.mark.parametrize("version", [None, "latest", "1.0", 1])
def test_bundledPrinterWithoutValidVersionLosesAndWarns(provider_class, tmp_path, bundled_root, version):
    bundled = writeBundledDefinition(bundled_root, "printer", version)
    installed = installedDefinition(tmp_path, "installed", "0.0.1")

    with patch("UM.Logger.Logger.warning") as warning:
        assert select(provider_class, [bundled, installed], mime = REAL_DEFINITION_MIME) == str(installed)
    assert warning.called


def test_bundledProfileOfUnknownDefinitionLoses(provider_class, tmp_path, bundled_root, upgrade_manager):
    bundled = writeBundledProfile(bundled_root, "quality", "printer_fine", "missing_printer")
    installed = writeBundledProfile(makePackage(tmp_path, "installed", "0.0.1", False), "quality", "printer_fine", "printer")

    assert select(provider_class, [bundled, installed], mime = REAL_INSTANCE_MIME) == str(installed)


def test_inheritanceCycleDoesNotHang(provider_class, tmp_path, bundled_root):
    first = writeBundledDefinition(bundled_root, "first", None, inherits = "second")
    writeBundledDefinition(bundled_root, "second", None, inherits = "first")
    installed = installedDefinition(tmp_path, "installed", "0.0.1", "first")

    assert select(provider_class, [first, installed], mime = REAL_DEFINITION_MIME) == str(installed)


def test_profileVersionOfItsOwnOverridesThePrinterVersion(provider_class, tmp_path, bundled_root, upgrade_manager):
    writeBundledDefinition(bundled_root, "printer", "1.0.0")
    changed = writeBundledProfile(bundled_root, "quality", "printer_fine", "printer", "1.2.0")
    unchanged = writeBundledProfile(bundled_root, "quality", "printer_coarse", "printer")
    installed_root = makePackage(tmp_path, "installed", "1.1.0", False)
    installed_fine = writeBundledProfile(installed_root, "quality", "printer_fine", "printer")
    installed_coarse = writeBundledProfile(installed_root, "quality", "printer_coarse", "printer")

    assert select(provider_class, [installed_fine, changed], mime = REAL_INSTANCE_MIME) == str(changed)
    assert select(provider_class, [unchanged, installed_coarse], mime = REAL_INSTANCE_MIME) == str(installed_coarse)


def test_profileWithOlderVersionOfItsOwnLosesEvenIfThePrinterIsNewer(provider_class, tmp_path, bundled_root, upgrade_manager):
    writeBundledDefinition(bundled_root, "printer", "2.0.0")
    stale = writeBundledProfile(bundled_root, "quality", "printer_fine", "printer", "1.0.0")
    installed = writeBundledProfile(makePackage(tmp_path, "installed", "1.5.0", False), "quality", "printer_fine", "printer")

    assert select(provider_class, [stale, installed], mime = REAL_INSTANCE_MIME) == str(installed)


def test_invalidVersionOfItsOwnFallsBackToThePrinterVersion(provider_class, tmp_path, bundled_root, upgrade_manager):
    writeBundledDefinition(bundled_root, "printer", "1.1.0")
    bundled = writeBundledProfile(bundled_root, "quality", "printer_fine", "printer", "garbage")
    installed = writeBundledProfile(makePackage(tmp_path, "installed", "1.0.0", False), "quality", "printer_fine", "printer")

    with patch("UM.Logger.Logger.warning") as warning:
        assert select(provider_class, [installed, bundled], mime = REAL_INSTANCE_MIME) == str(bundled)
    assert warning.called


def test_extruderVersionOfItsOwnOverridesTheMachineVersion(provider_class, tmp_path, bundled_root):
    writeBundledDefinition(bundled_root, "printer", "1.0.0")
    (bundled_root / "extruders").mkdir()
    bundled = bundled_root / "extruders" / "printer_extruder_0.def.json"
    bundled.write_text(json.dumps({"version": 2, "name": "Extruder", "metadata": {"machine": "printer", "package_version": "1.3.0"}, "settings": {}}), encoding = "utf-8")
    installed = installedDefinition(tmp_path, "installed", "1.2.0", "printer_extruder_0")

    assert select(provider_class, [installed, bundled], mime = REAL_DEFINITION_MIME) == str(bundled)
