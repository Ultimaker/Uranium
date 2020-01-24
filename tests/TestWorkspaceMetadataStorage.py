# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Workspace.WorkspaceMetadataStorage import WorkspaceMetadataStorage


def test_setEntryToStore():
    storage = WorkspaceMetadataStorage()
    storage.setEntryToStore("test", "bloop", 12)
    assert storage.getPluginMetadata("test") == {"bloop": 12}


def test_setNestedEntryToStore():
    storage = WorkspaceMetadataStorage()
    storage.setEntryToStore("test", "bloop", {"zomg": "blorp"})
    assert storage.getPluginMetadata("test") == {"bloop": {"zomg": "blorp"}}


def test_setMultipleEntriesToStore():
    storage = WorkspaceMetadataStorage()
    storage.setEntryToStore("test", "bloop", 13)
    storage.setEntryToStore("test", "bloop2", 32)

    metadata = storage.getPluginMetadata("test")
    assert len(metadata.keys()) == 2
    assert metadata["bloop"] == 13
    assert metadata["bloop2"] == 32


def test_getUnknownEntry():
    storage = WorkspaceMetadataStorage()
    storage.setEntryToStore("test", "bloop", 12)
    assert storage.getPluginMetadata("unknown") == {}


def test_setAllDataAndClear():
    storage = WorkspaceMetadataStorage()
    storage.setAllData({"zomg": {"value": "zomg"}})
    assert storage.getPluginMetadata("zomg") == {"value": "zomg"}

    storage.clear()
    assert storage.getPluginMetadata("zomg") == {}


def test_getAllData():
    storage = WorkspaceMetadataStorage()
    storage.setEntryToStore("test", "bloop", 13)
    storage.setEntryToStore("test_2", "bloop", 34)

    data = storage.getAllData()
    assert len(data.keys()) == 2
    assert data["test"]["bloop"] == 13
    assert data["test_2"]["bloop"] == 34