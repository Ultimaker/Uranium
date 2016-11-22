# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QCoreApplication, QUrl, QSizeF
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QFontDatabase, QFontInfo
from PyQt5.QtQml import QQmlComponent, QQmlContext

import json
import os
import os.path
import sys

from UM.Logger import Logger
from UM.Resources import Resources
from UM.Preferences import Preferences
from UM.Application import Application
from UM.Decorators import deprecated

class Theme(QObject):
    def __init__(self, engine, parent = None):
        super().__init__(parent)

        self._engine = engine
        self._styles = None
        self._path = ""
        self._icons = {}
        self._images = {}

        # Workaround for incorrect default font on Windows
        if sys.platform == "win32":
            default_font = QFont()
            default_font.setPointSize(9)
            QCoreApplication.instance().setFont(default_font)

        self._em_height = int(QFontMetrics(QCoreApplication.instance().font()).ascent())
        self._em_width = self._em_height;

        self._initializeDefaults()

        Preferences.getInstance().addPreference("general/theme", Application.getInstance().getApplicationName())
        try:
            theme_path = Resources.getPath(Resources.Themes, Preferences.getInstance().getValue("general/theme"))
            self.load(theme_path)
        except FileNotFoundError:
            Logger.log("e", "Could not find theme file.")

    themeLoaded = pyqtSignal()

    @pyqtSlot(str, result = "QColor")
    def getColor(self, color):
        if color in self._colors:
            return self._colors[color]

        Logger.log("w", "No color %s defined in Theme", color)
        return QColor()

    @pyqtSlot(str, result = "QSizeF")
    def getSize(self, size):
        if size in self._sizes:
            return self._sizes[size]

        Logger.log("w", "No size %s defined in Theme", size)
        return QSizeF()

    @pyqtSlot(str, result = "QUrl")
    def getIcon(self, icon_name):
        if icon_name in self._icons:
            return self._icons[icon_name]

        Logger.log("w", "No icon %s defined in Theme", icon_name)
        return QUrl()

    @pyqtSlot(str, result = "QUrl")
    def getImage(self, image_name):
        if image_name in self._images:
            return self._images[image_name]

        Logger.log("w", "No image %s defined in Theme", image_name)
        return QUrl()

    @pyqtSlot(str, result = "QFont")
    def getFont(self, font_name):
        if font_name in self._fonts:
            return self._fonts[font_name]

        Logger.log("w", "No font %s defined in Theme", font_name)
        return QFont()

    @pyqtProperty(QObject, notify = themeLoaded)
    def styles(self):
        return self._styles

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    @deprecated("Use getIcon for performance reasons", "2.1")
    def icons(self):
        return self._icons

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    @deprecated("Use getImage for performance reasons", "2.1")
    def images(self):
        return self._images

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    @deprecated("Use getColor for performance reasons", "2.1")
    def colors(self):
        return self._colors

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    @deprecated("Use getFont for performance reasons", "2.1")
    def fonts(self):
        return self._fonts

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    @deprecated("Use getSize for performance reasons", "2.1")
    def sizes(self):
        return self._sizes

    @pyqtSlot(str)
    def load(self, path):
        if path == self._path:
            return

        self._path = path

        with open(os.path.join(self._path, "theme.json")) as f:
            Logger.log("d", "Loading theme file: %s", os.path.join(self._path, "theme.json"))
            data = json.load(f)

        self._initializeDefaults()

        if "colors" in data:
            for name, color in data["colors"].items():
                c = QColor(color[0], color[1], color[2], color[3])
                self._colors[name] = c

        fontsdir = os.path.join(self._path, "fonts")
        if os.path.isdir(fontsdir):
            for file in os.listdir(fontsdir):
                if "ttf" in file:
                    QFontDatabase.addApplicationFont(os.path.join(fontsdir, file))

        if "fonts" in data:
            for name, font in data["fonts"].items():
                f = QFont()
                f.setFamily(font.get("family", QCoreApplication.instance().font().family()))

                f.setBold(font.get("bold", False))
                f.setLetterSpacing(QFont.AbsoluteSpacing, font.get("letterSpacing", 0))
                f.setItalic(font.get("italic", False))
                f.setPixelSize(font.get("size", 1) * self._em_height)
                f.setCapitalization(QFont.AllUppercase if font.get("capitalize", False) else QFont.MixedCase)

                self._fonts[name] = f

        if "sizes" in data:
            for name, size in data["sizes"].items():
                s = QSizeF()
                s.setWidth(round(size[0] * self._em_width))
                s.setHeight(round(size[1] * self._em_height))

                self._sizes[name] = s

        iconsdir = os.path.join(self._path, "icons")
        if os.path.isdir(iconsdir):
            for icon in os.listdir(iconsdir):
                name = os.path.splitext(icon)[0]
                self._icons[name] = QUrl.fromLocalFile(os.path.join(iconsdir, icon))

        imagesdir = os.path.join(self._path, "images")
        if os.path.isdir(imagesdir):
            for image in os.listdir(imagesdir):
                name = os.path.splitext(image)[0]
                self._images[name] = QUrl.fromLocalFile(os.path.join(imagesdir, image))

        styles = os.path.join(self._path, "styles.qml")
        if os.path.isfile(styles):
            c = QQmlComponent(self._engine, styles)
            context = QQmlContext(self._engine, self._engine)
            context.setContextProperty("Theme", self)
            self._styles = c.create(context)

            if c.isError():
                for error in c.errors():
                    Logger.log("e", error.toString())

        Logger.log("d", "Loaded theme %s", self._path)
        self.themeLoaded.emit()

    def _initializeDefaults(self):
        self._fonts = {
            "system": QCoreApplication.instance().font(),
            "fixed": QFontDatabase.systemFont(QFontDatabase.FixedFont)
        }

        palette = QCoreApplication.instance().palette()
        self._colors = {
            "system_window": palette.window(),
            "system_text": palette.text()
        }

        self._sizes = {
            "line": QSizeF(self._em_width, self._em_height)
        }

def createTheme(engine, script_engine):
    return Theme(engine)

