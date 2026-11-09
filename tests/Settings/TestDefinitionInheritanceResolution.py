# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from UM.Resources import Resources
from UM.Settings.DefinitionContainer import DefinitionContainer


@pytest.fixture(autouse = True)
def restore_search_paths():
    paths = list(Resources._Resources__paths)
    yield
    Resources._Resources__paths[:] = paths


def writeDefinition(root, name, setting_default, inherits = None):
    folder = root / "definitions"
    folder.mkdir(parents = True, exist_ok = True)
    data = {"version": 2, "name": name, "metadata": {}}
    if inherits:
        data["inherits"] = inherits
        data["overrides"] = {}
        data["settings"] = {}
    else:
        data["settings"] = {"test_setting": {"label": "Test", "description": "A test setting", "default_value": setting_default, "type": "int"}}
    path = folder / f"{name}.def.json"
    path.write_text(json.dumps(data), encoding = "utf-8")
    return str(path)


def loadChild(child_path):
    container = DefinitionContainer("child")
    with open(child_path, encoding = "utf-8") as f:
        container.deserialize(f.read(), child_path)
    return container


def test_parentIsLoadedFromTheFileTheRegistryChose(tmp_path, upgrade_manager):
    first = tmp_path / "first"
    second = tmp_path / "second"
    writeDefinition(first, "base", 1)
    writeDefinition(second, "base", 2)
    child_path = writeDefinition(first, "child", None, inherits = "base")
    Resources.addSearchPath(str(first))
    Resources.addSearchPath(str(second))

    registry = MagicMock()
    registry.getContainerFilePathById.return_value = str(second / "definitions" / "base.def.json")
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", return_value = registry):
        container = loadChild(child_path)

    registry.getContainerFilePathById.assert_called_with("base")
    assert container.getProperty("test_setting", "default_value") == 2
    assert str(second / "definitions" / "base.def.json") in container.getInheritedFiles()
    assert str(first / "definitions" / "base.def.json") not in container.getInheritedFiles()


def test_parentFallsBackToSearchOrderWhenRegistryDoesNotKnowIt(tmp_path, upgrade_manager):
    first = tmp_path / "first"
    second = tmp_path / "second"
    writeDefinition(first, "base", 1)
    writeDefinition(second, "base", 2)
    child_path = writeDefinition(second, "child", None, inherits = "base")
    Resources.addSearchPath(str(first))
    Resources.addSearchPath(str(second))

    registry = MagicMock()
    registry.getContainerFilePathById.return_value = None
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", return_value = registry):
        container = loadChild(child_path)

    assert container.getProperty("test_setting", "default_value") == 1


def test_parentFallsBackToSearchOrderWithoutRegistry(tmp_path, upgrade_manager):
    first = tmp_path / "first"
    writeDefinition(first, "base", 1)
    child_path = writeDefinition(first, "child", None, inherits = "base")
    Resources.addSearchPath(str(first))

    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", return_value = None):
        container = loadChild(child_path)

    assert container.getProperty("test_setting", "default_value") == 1


def test_registryPathThatNoLongerExistsFallsBack(tmp_path, upgrade_manager):
    first = tmp_path / "first"
    writeDefinition(first, "base", 1)
    child_path = writeDefinition(first, "child", None, inherits = "base")
    Resources.addSearchPath(str(first))

    registry = MagicMock()
    registry.getContainerFilePathById.return_value = str(tmp_path / "gone" / "definitions" / "base.def.json")
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", return_value = registry):
        container = loadChild(child_path)

    assert container.getProperty("test_setting", "default_value") == 1


def test_providerWithoutPathSupportFallsBack(tmp_path, upgrade_manager):
    first = tmp_path / "first"
    writeDefinition(first, "base", 1)
    child_path = writeDefinition(first, "child", None, inherits = "base")
    Resources.addSearchPath(str(first))

    registry = MagicMock()
    registry.getContainerFilePathById.side_effect = NotImplementedError()
    with patch("UM.Settings.ContainerRegistry.ContainerRegistry.getInstance", return_value = registry):
        container = loadChild(child_path)

    assert container.getProperty("test_setting", "default_value") == 1
