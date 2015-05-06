# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QCoreApplication, QUrl, QSizeF
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QFontDatabase, QFontInfo
from PyQt5.QtQml import QQmlComponent

import json
import os
import os.path

from UM.Logger import Logger
from UM.Resources import Resources

class Theme(QObject):
    def __init__(self, engine, parent = None):
        super().__init__(parent)

        self._engine = engine
        self._styles = None
        self._path = ""
        self._icons = {}
        self._images = {}

        self._em_height = int(QFontMetrics(QCoreApplication.instance().font()).ascent())
        self._em_width = self._em_height;

        self._initializeDefaults()

    themeLoaded = pyqtSignal()

    @pyqtProperty(QObject, notify = themeLoaded)
    def styles(self):
        return self._styles

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    def icons(self):
        return self._icons

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    def images(self):
        return self._images

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    def colors(self):
        return self._colors

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    def fonts(self):
        return self._fonts

    @pyqtProperty("QVariantMap", notify = themeLoaded)
    def sizes(self):
        return self._sizes

    @pyqtSlot(QUrl)
    def load(self, path):
        self._path = path.toLocalFile()

        with open(os.path.join(self._path, "theme.json")) as f:
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
                f.setStyleName(font.get("style", "Regular"))
                f.setBold(font.get("bold", False))
                f.setItalic(font.get("italic", False))
                f.setPixelSize(int(font.get("size", 1) * self._em_height))
                f.setCapitalization(QFont.AllUppercase if font.get("capitalize", False) else QFont.MixedCase)

                self._fonts[name] = f

        if "sizes" in data:
            for name, size in data["sizes"].items():
                s = QSizeF()
                s.setWidth(size[0] * self._em_width)
                s.setHeight(size[1] * self._em_height)

                self._sizes[name] = s

        styles = os.path.join(self._path, "styles.qml")
        if os.path.isfile(styles):
            c = QQmlComponent(self._engine, styles)
            self._styles = c.create()

            if c.isError():
                for error in c.errors():
                    Logger.log("e", error.toString())

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

        Logger.log("d", "Loaded theme %s", self._path)
        self.themeLoaded.emit()

    def _initializeDefaults(self):
        self._fonts = {
            "system": QCoreApplication.instance().font()
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

