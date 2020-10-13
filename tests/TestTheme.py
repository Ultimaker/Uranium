from UM.Qt.Bindings.Theme import Theme
from unittest.mock import MagicMock, patch
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QSizeF, QUrl
import pytest
import os

@pytest.fixture
def theme():
    application = MagicMock()
    with patch("UM.Qt.Bindings.Theme.QFontMetrics"):
        with patch("UM.Qt.Bindings.Theme.QCoreApplication.instance"):
            with patch("UM.Application.Application.getInstance", MagicMock(return_value = application)):
                with patch("UM.Resources.Resources.getPath", MagicMock(return_value = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_theme"))):
                    return Theme(MagicMock())


def test_getColor(theme):
    assert theme.getColor("test_color") == QColor(255, 255, 255, 255)


def test_getUnknownColor(theme):
    assert theme.getColor("Dunno") == QColor()


def test_getKnownSize(theme):
    assert theme.getSize("test_size") == QSizeF(42, 1337)


def test_getUnknownSize(theme):
    assert theme.getSize("Dunno?") == QSizeF()


def test_getKnownIcon(theme):
    icon_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_theme", "icons", "test.svg")
    assert theme.getIcon("test") == QUrl.fromLocalFile(icon_location)


def test_getUnknownIcon(theme):
    assert theme.getIcon("BoringAndProfesisonalIcon") == QUrl()


def test_knownFont(theme):
    font = theme.getFont("test_font")
    assert font.family() == "Felidae"
    assert font.weight() == 40


def test_unknownFont(theme):
    assert theme.getFont("whatever") == QFont()


def test_knownImage(theme):
    image_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_theme", "images", "kitten.jpg")
    assert theme.getImage("kitten") == QUrl.fromLocalFile(image_location)


def test_unknownImage(theme):
    assert theme.getImage("BoringBusinessPictureWhichIsAbsolutelyNotAKitten") == QUrl()
