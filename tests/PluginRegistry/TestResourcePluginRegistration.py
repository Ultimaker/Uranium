# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

import json
from unittest.mock import patch

import pytest

from UM.Resources import Resources
from UM.SemanticVersion import SemanticVersion


@pytest.fixture(autouse = True)
def restore_resources_state():
    paths = list(Resources._Resources__paths)
    packages = dict(Resources._Resources__packages)
    yield
    Resources._Resources__paths[:] = paths
    Resources._Resources__packages.clear()
    Resources._Resources__packages.update(packages)


def writePlugin(location, plugin_id, **overrides):
    plugin_dir = location / plugin_id
    (plugin_dir / "definitions").mkdir(parents = True)
    info = {"name": plugin_id, "package_type": "definitions", "version": "1.2.3", "api": 8, "supported_sdk_versions": ["8.0.0"]}
    info.update(overrides)
    info = {key: value for key, value in info.items() if value is not None}
    (plugin_dir / "plugin.json").write_text(json.dumps(info), encoding = "utf-8")
    return plugin_dir


@pytest.fixture
def registry(plugin_registry, tmp_path):
    plugin_registry._plugin_locations = [str(tmp_path)]
    return plugin_registry


def test_resourcePluginIsRegisteredWithItsVersion(registry, tmp_path):
    plugin_dir = writePlugin(tmp_path, "my_printer", version = "1.2.3-rc.1+meta")
    registry._bundled_plugin_cache["my_printer"] = False

    assert registry._registerResourcePlugin("my_printer")

    package = Resources.getPackageForPath(str(plugin_dir / "definitions" / "printer.def.json"))
    assert package is not None
    assert package.package_id == "my_printer"
    assert package.version == SemanticVersion("1.2.3-rc.1")
    assert not package.is_bundled


def test_bundledResourcePluginIsMarkedAsBundled(registry, tmp_path):
    plugin_dir = writePlugin(tmp_path, "my_printer")
    registry._bundled_plugin_cache["my_printer"] = True

    assert registry._registerResourcePlugin("my_printer")

    assert Resources.getPackageForPath(str(plugin_dir)).is_bundled


@pytest.mark.parametrize("version", [None, "", "1.2", "v1.2.3", "1.2.3.4", 1, ["1.2.3"], "latest"])
def test_invalidVersionIsRejected(registry, tmp_path, version):
    plugin_dir = writePlugin(tmp_path, "my_printer", version = version)
    registry._bundled_plugin_cache["my_printer"] = False

    with patch("UM.PluginRegistry.Logger") as logger:
        assert registry._registerResourcePlugin("my_printer")  # Still a resource plugin, so it is not loaded as code.

    assert Resources.getPackageForPath(str(plugin_dir)) is None
    assert str(plugin_dir) not in Resources._Resources__paths
    assert logger.error.called or logger.warning.called


def test_disabledResourcePluginIsNotRegistered(registry, tmp_path):
    plugin_dir = writePlugin(tmp_path, "my_printer")
    registry._disabled_plugins = ["my_printer"]

    assert registry._registerResourcePlugin("my_printer")

    assert Resources.getPackageForPath(str(plugin_dir)) is None


def test_incompatibleApiResourcePluginIsNotRegistered(registry, tmp_path):
    plugin_dir = writePlugin(tmp_path, "my_printer", api = 5, supported_sdk_versions = ["5.0.0"])

    assert registry._registerResourcePlugin("my_printer")

    assert Resources.getPackageForPath(str(plugin_dir)) is None
    assert "my_printer" in registry._outdated_plugins


def test_codePluginIsNotAResourcePlugin(registry, tmp_path):
    plugin_dir = writePlugin(tmp_path, "my_code", package_type = "plugin")

    assert not registry._registerResourcePlugin("my_code")

    assert Resources.getPackageForPath(str(plugin_dir)) is None
