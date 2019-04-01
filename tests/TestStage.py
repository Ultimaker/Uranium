from PyQt5.QtCore import QUrl

from UM.Stage import Stage


def test_addGetDisplayComponent():
    stage = Stage()
    stage.addDisplayComponent("BLORP", "location")
    assert stage.getDisplayComponent("BLORP") == QUrl.fromLocalFile("location")

    stage.addDisplayComponent("MEEP!", QUrl.fromLocalFile("MEEP"))
    assert stage.getDisplayComponent("MEEP!") == QUrl.fromLocalFile("MEEP")


def test_iconSource():
    stage = Stage()

    # Should be empty if we didn't do anything yet
    assert stage.iconSource == QUrl()

    stage.setIconSource("DERP")
    assert stage.iconSource == QUrl.fromLocalFile("DERP")

    stage.setIconSource(QUrl.fromLocalFile("FOO"))
    assert stage.iconSource == QUrl.fromLocalFile("FOO")


def test_getUnknownDisplayComponent():
    stage = Stage()
    # Just an empty QUrl
    assert stage.getDisplayComponent("BLORP") == QUrl()