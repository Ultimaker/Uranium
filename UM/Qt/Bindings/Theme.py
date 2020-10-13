# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os
import sys
from typing import Dict, Optional, List

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, QCoreApplication, QUrl, QSizeF
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QFontDatabase
from PyQt5.QtQml import QQmlComponent, QQmlContext

import UM.Application
from UM.FlameProfiler import pyqtSlot
from UM.Logger import Logger
from UM.Resources import Resources


class Theme(QObject):
    def __init__(self, engine, parent = None) -> None:
        super().__init__(parent)

        self._engine = engine
        self._styles = None  # type: Optional[QObject]
        self._path = ""
        self._icons = {}  # type: Dict[str, QUrl]
        self._images = {}  # type: Dict[str, QUrl]

        # Workaround for incorrect default font on Windows
        if sys.platform == "win32":
            default_font = QFont()
            default_font.setPointSize(9)
            QCoreApplication.instance().setFont(default_font)

        self._em_height = int(QFontMetrics(QCoreApplication.instance().font()).ascent())
        self._em_width = self._em_height

        # Cache the initial language in the preferences. For fonts, a special font can be defined with, for example,
        # "medium" and "medium_nl_NL". If the special one exists, getFont() will return that, otherwise the default
        # will be returned. We cache the initial language here is because Cura can only change its language if it gets
        # restarted, so we need to keep the fonts consistent in a single Cura run.
        self._preferences = UM.Application.Application.getInstance().getPreferences()
        self._lang_code = self._preferences.getValue("general/language")

        self._initializeDefaults()

        self.reload()

    themeLoaded = pyqtSignal()

    def reload(self):
        self._styles = None
        self._path = ""
        self._icons = {}
        self._images = {}
        application = UM.Application.Application.getInstance()
        application.getPreferences().addPreference("general/theme", application.default_theme)
        try:
            theme_path = Resources.getPath(Resources.Themes, application.getPreferences().getValue("general/theme"))
            self.load(theme_path)
        except FileNotFoundError:
            Logger.log("e", "Could not find theme file, resetting to the default theme.")

            # cannot the current theme, so go back to the default
            application.getPreferences().setValue("general/theme", application.default_theme)
            theme_path = Resources.getPath(Resources.Themes, application.getPreferences().getValue("general/theme"))
            self.load(theme_path)

    @pyqtSlot(result = "QVariantList")
    def getThemes(self) -> List[Dict[str, str]]:
        themes = []
        for path in Resources.getAllPathsForType(Resources.Themes):
            try:
                for file in os.listdir(path):
                    folder = os.path.join(path, file)
                    theme_file = os.path.join(folder, "theme.json")
                    if os.path.isdir(folder) and os.path.isfile(theme_file):
                        theme_id = os.path.basename(folder)

                        with open(theme_file, encoding = "utf-8") as f:
                            try:
                                data = json.load(f)
                            except (UnicodeDecodeError, json.decoder.JSONDecodeError):
                                Logger.log("w", "Could not parse theme %s", theme_id)
                                continue # do not add this theme to the list, but continue looking for other themes

                            try:
                                theme_name = data["metadata"]["name"]
                            except KeyError:
                                Logger.log("w", "Theme %s does not have a name; using its id instead", theme_id)
                                theme_name = theme_id # fallback if no name is specified in json

                        themes.append({
                            "id": theme_id,
                            "name": theme_name
                        })
            except EnvironmentError:
                pass
        themes.sort(key = lambda k: k["name"])

        return themes

    @pyqtSlot(str, result = "QColor")
    def getColor(self, color: str) -> QColor:
        if color in self._colors:
            return self._colors[color]

        Logger.log("w", "No color %s defined in Theme", color)
        return QColor()

    @pyqtSlot(str, result = "QSizeF")
    def getSize(self, size) -> QSizeF:
        if size in self._sizes:
            return self._sizes[size]

        Logger.log("w", "No size %s defined in Theme", size)
        return QSizeF()

    @pyqtSlot(str, result = "QUrl")
    def getIcon(self, icon_name: str) -> QUrl:
        if icon_name in self._icons:
            return self._icons[icon_name]

        # We don't log this anymore since we have new fallback behavior to load the icon from a plugin folder
        # Logger.log("w", "No icon %s defined in Theme", icon_name)
        return QUrl()

    @pyqtSlot(str, result = "QUrl")
    def getImage(self, image_name: str) -> QUrl:
        if image_name in self._images:
            return self._images[image_name]

        Logger.log("w", "No image %s defined in Theme", image_name)
        return QUrl()

    @pyqtSlot(str, result = "QFont")
    def getFont(self, font_name: str) -> QFont:
        lang_specific_font_name = "%s_%s" % (font_name, self._lang_code)
        if lang_specific_font_name in self._fonts:
            return self._fonts[lang_specific_font_name]

        if font_name in self._fonts:
            return self._fonts[font_name]

        Logger.log("w", "No font %s defined in Theme", font_name)
        return QFont()

    @pyqtProperty(QObject, notify = themeLoaded)
    def styles(self):
        return self._styles

    @pyqtSlot(str)
    def load(self, path: str, is_first_call: bool = True) -> None:
        if path == self._path:
            return

        theme_full_path = os.path.join(path, "theme.json")
        Logger.log("d", "Loading theme file: {theme_full_path}".format(theme_full_path = theme_full_path))
        try:
            with open(theme_full_path, encoding = "utf-8") as f:
                data = json.load(f)
        except EnvironmentError as e:
            Logger.error("Unable to load theme file at {theme_full_path}: {err}".format(theme_full_path = theme_full_path, err = e))
            return
        except UnicodeDecodeError:
            Logger.error("Theme file at {theme_full_path} is corrupt (invalid UTF-8 bytes).".format(theme_full_path = theme_full_path))
            return
        except json.JSONDecodeError:
            Logger.error("Theme file at {theme_full_path} is corrupt (invalid JSON syntax).".format(theme_full_path = theme_full_path))
            return

        # Iteratively load inherited themes
        try:
            theme_id = data["metadata"]["inherits"]
            self.load(Resources.getPath(Resources.Themes, theme_id), is_first_call = False)
        except FileNotFoundError:
            Logger.log("e", "Could not find inherited theme %s", theme_id)
        except KeyError:
            pass  # No metadata or no inherits keyword in the theme.json file

        if "colors" in data:
            for name, color in data["colors"].items():
                try:
                    c = QColor(color[0], color[1], color[2], color[3])
                except IndexError:  # Color doesn't have enough components.
                    Logger.log("w", "Colour {name} doesn't have enough components. Need to have 4, but had {num_components}.".format(name = name, num_components = len(color)))
                    continue  # Skip this one then.
                self._colors[name] = c

        fonts_dir = os.path.join(path, "fonts")
        if os.path.isdir(fonts_dir):
            for root, dirnames, filenames in os.walk(fonts_dir):
                for filename in filenames:
                    if filename.lower().endswith(".ttf"):
                        QFontDatabase.addApplicationFont(os.path.join(root, filename))

        if "fonts" in data:
            system_font_size = QCoreApplication.instance().font().pointSize()
            for name, font in data["fonts"].items():
                q_font = QFont()
                q_font.setFamily(font.get("family", QCoreApplication.instance().font().family()))

                if font.get("bold"):
                    q_font.setBold(font.get("bold", False))
                else:
                    q_font.setWeight(font.get("weight", 50))

                q_font.setLetterSpacing(QFont.AbsoluteSpacing, font.get("letterSpacing", 0))
                q_font.setItalic(font.get("italic", False))
                q_font.setPointSize(int(font.get("size", 1) * system_font_size))
                q_font.setCapitalization(QFont.AllUppercase if font.get("capitalize", False) else QFont.MixedCase)

                self._fonts[name] = q_font

        if "sizes" in data:
            for name, size in data["sizes"].items():
                s = QSizeF()
                s.setWidth(round(size[0] * self._em_width))
                s.setHeight(round(size[1] * self._em_height))

                self._sizes[name] = s

        iconsdir = os.path.join(path, "icons")
        if os.path.isdir(iconsdir):
            for icon in os.listdir(iconsdir):
                name = os.path.splitext(icon)[0]
                self._icons[name] = QUrl.fromLocalFile(os.path.join(iconsdir, icon))

        imagesdir = os.path.join(path, "images")
        if os.path.isdir(imagesdir):
            for image in os.listdir(imagesdir):
                name = os.path.splitext(image)[0]
                self._images[name] = QUrl.fromLocalFile(os.path.join(imagesdir, image))

        styles = os.path.join(path, "styles.qml")
        if os.path.isfile(styles):
            c = QQmlComponent(self._engine, styles)
            context = QQmlContext(self._engine, self._engine)
            context.setContextProperty("Theme", self)
            self._styles = c.create(context)

            if c.isError():
                for error in c.errors():
                    Logger.log("e", error.toString())

        Logger.log("d", "Loaded theme %s", path)
        self._path = path

        # only emit the theme loaded signal once after all the themes in the inheritance chain have been loaded
        if is_first_call:
            self.themeLoaded.emit()

    def _initializeDefaults(self) -> None:
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

    @classmethod
    def getInstance(cls, engine = None) -> "Theme":
        """Get the singleton instance for this class."""

        # Note: Explicit use of class name to prevent issues with inheritance.
        if Theme.__instance is None:
            Theme.__instance = cls(engine)
        return Theme.__instance

    __instance = None   # type: "Theme"


def createTheme(engine, script_engine = None):
    return Theme.getInstance(engine)

