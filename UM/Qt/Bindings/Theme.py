# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os
import sys
import warnings
from typing import Dict, List

from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication, QUrl, QSizeF
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QFontDatabase

import UM.Application
from UM.FlameProfiler import pyqtSlot
from UM.Logger import Logger
from UM.Resources import Resources
from UM.Trust import TrustBasics


class Theme(QObject):
    def __init__(self, engine, parent = None) -> None:
        super().__init__(parent)

        self._engine = engine
        self._path = ""
        self._icons = {}  # type: Dict[str, Dict[str, QUrl]]
        self._deprecated_icons = {} # type: Dict[str, Dict[str, str]]
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

        self._check_if_trusted = False
        self.reload()

    themeLoaded = pyqtSignal()

    def reload(self):
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

    def setCheckIfTrusted(self, check_if_trusted: bool):
        """Set: Can themes from unbundled locations be selected, or only the ones packaged with the app?"""
        self._check_if_trusted = check_if_trusted

    @pyqtSlot(result = "QVariantList")
    def getThemes(self) -> List[Dict[str, str]]:
        install_prefix = os.path.abspath(UM.Application.Application.getInstance().getInstallPrefix())

        themes = []
        for path in Resources.getAllPathsForType(Resources.Themes):
            if self._check_if_trusted and not TrustBasics.isPathInLocation(install_prefix, path):
                # This will prevent themes to load from outside 'bundled' folders, when `check_if_trusted` is True.
                # Note that this will be a lot less useful in newer versions supporting Qt 6, due to lack of QML Styles.
                Logger.warning("Skipped indexing Theme from outside bundled folders: ", path)
                continue
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

    @pyqtSlot(str, str, result = "QUrl")
    @pyqtSlot(str, result = "QUrl")
    def getIcon(self, icon_name: str, detail_level: str = "default") -> QUrl:
        """
        Finds and returns the url of the requested icon. The icons are organized in folders according to their detail
        level and the same icon may exist with more details. If a detail level is not specified, the icon will be
        retrieved from the "default" folder. Icons with a higher detail level are recommended to be used with a bigger
        width/height.

        :param icon_name: The name of the icon to be retrieved. The same icon may exist in multiple detail levels.
        :param detail_level: The level of detail of the icon. Choice between "low, "default", "medium", "high".
        :return: The file url of the requested icon, in the requested detail level.
        """
        if detail_level in self._icons:
            if icon_name in self._icons[detail_level]:
                return self._icons[detail_level][icon_name]
        elif icon_name in self._icons["icons"]:  # Retrieve the "old" icon from the base icon folder
            return self._icons["icons"][icon_name]

        if icon_name in self._deprecated_icons:
            new_icon = self._deprecated_icons[icon_name]["new_icon"]
            warning = f"The icon '{icon_name}' is deprecated. Please use icon '{new_icon}' instead."

            Logger.log("w_once", warning)
            warnings.warn(warning, DeprecationWarning, stacklevel=2)
            return self.getIcon(self._deprecated_icons[icon_name]["new_icon"], self._deprecated_icons[icon_name]["size"])

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
            for name, value in data["colors"].items():

                if not is_first_call and isinstance(value, str):
                    # Keep parent theme string colors as strings and parse later
                    self._colors[name] = value
                    continue

                if isinstance(value, str) and is_first_call:
                    # value is reference to base_colors color name
                    try:
                        color = data["base_colors"][value]
                    except IndexError:
                        Logger.log("w", "Colour {value} could not be found in base_colors".format(value = value))
                        continue
                else:
                    color = value

                try:
                    c = QColor(color[0], color[1], color[2], color[3])
                except IndexError:  # Color doesn't have enough components.
                    Logger.log("w", "Colour {name} doesn't have enough components. Need to have 4, but had {num_components}.".format(name = name, num_components = len(color)))
                    continue  # Skip this one then.
                self._colors[name] = c

        if "base_colors" in data:
            for name, color in data["base_colors"].items():
                try:
                    c = QColor(color[0], color[1], color[2], color[3])
                except IndexError:  # Color doesn't have enough components.
                    Logger.log("w", "Colour {name} doesn't have enough components. Need to have 4, but had {num_components}.".format(name = name, num_components = len(color)))
                    continue  # Skip this one then.
                self._colors[name] = c

        if is_first_call and self._colors:
            #Convert all string value colors to their referenced color
            for name, color in self._colors.items():
                if isinstance(color, str):
                    try:
                        c = self._colors[color]
                        self._colors[name] = c
                    except:
                        Logger.log("w", "Colour {name} {color} does".format(name = name, color = color))


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
                    q_font.setWeight(font.get("weight", 500))

                q_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, font.get("letterSpacing", 0))
                q_font.setItalic(font.get("italic", False))
                q_font.setPointSize(int(font.get("size", 1) * system_font_size))
                q_font.setCapitalization(QFont.Capitalization.AllUppercase if font.get("capitalize", False) else QFont.Capitalization.MixedCase)

                self._fonts[name] = q_font

        if "sizes" in data:
            for name, size in data["sizes"].items():
                s = QSizeF()
                s.setWidth(round(size[0] * self._em_width))
                s.setHeight(round(size[1] * self._em_height))

                self._sizes[name] = s

        iconsdir = os.path.join(path, "icons")
        if os.path.isdir(iconsdir):
            try:
                for base_path, _, icons in os.walk(iconsdir):
                    detail_level = base_path.split(os.sep)[-1]
                    if detail_level not in self._icons:
                        self._icons[detail_level] = {}
                    for icon in icons:
                        name = os.path.splitext(icon)[0]
                        self._icons[detail_level][name] = QUrl.fromLocalFile(os.path.join(base_path, icon))
            except EnvironmentError as err:  # Exception when calling os.walk, e.g. no access rights.
                Logger.error(f"Can't access icons of theme ({iconsdir}): {err}")
                # Won't get any icons then. Images will show as black squares.

            deprecated_icons_file = os.path.join(iconsdir, "deprecated_icons.json")
            if os.path.isfile(deprecated_icons_file):
                try:
                    with open(deprecated_icons_file, encoding="utf-8") as f:
                        data = json.load(f)
                        for icon in data:
                            self._deprecated_icons[icon] = data[icon]
                except (UnicodeDecodeError, json.decoder.JSONDecodeError, EnvironmentError):
                    Logger.logException("w", "Could not parse deprecated icons list %s", deprecated_icons_file)

        imagesdir = os.path.join(path, "images")
        if os.path.isdir(imagesdir):
            try:
                for image in os.listdir(imagesdir):
                    name = os.path.splitext(image)[0]
                    self._images[name] = QUrl.fromLocalFile(os.path.join(imagesdir, image))
            except EnvironmentError as err:  # Exception when calling os.listdir, e.g. no access rights.
                Logger.error(f"Can't access image of theme ({imagesdir}): {err}")
                # Won't get any images then. They will show as black squares.

        Logger.log("d", "Loaded theme %s", path)
        Logger.info(f"System's em size is {self._em_height}px.")
        self._path = path

        # only emit the theme loaded signal once after all the themes in the inheritance chain have been loaded
        if is_first_call:
            self.themeLoaded.emit()

    def _initializeDefaults(self) -> None:
        self._fonts = {
            "system": QCoreApplication.instance().font(),
            "fixed": QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
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
