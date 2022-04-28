from PyQt6.QtCore import QUrl

from UM.Stage import Stage


def test_addGetDisplayComponent():
    stage = Stage()
    stage.addDisplayComponent("BLORP", "location")
    assert stage.getDisplayComponent("BLORP") == QUrl.fromLocalFile("location")

    stage.addDisplayComponent("MEEP!", QUrl.fromLocalFile("MEEP"))
    assert stage.getDisplayComponent("MEEP!") == QUrl.fromLocalFile("MEEP")


def test_getUnknownDisplayComponent():
    stage = Stage()
    # Just an empty QUrl
    assert stage.getDisplayComponent("BLORP") == QUrl()
