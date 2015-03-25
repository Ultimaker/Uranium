from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QCoreApplication, QUrl, QSizeF
from PyQt5.QtGui import QColor, QFont, QFontMetrics
from PyQt5.QtQml import QQmlComponent

import json
import os.path

from UM.Logger import Logger
from UM.Resources import Resources

class Theme(QObject):
    def __init__(self, engine, parent = None):
        super().__init__(parent)

        self._engine = engine

        self._fonts = {}
        self._colors = {}
        self._sizes = {}

        self._styles = None

        self._path = ""

        self._line_height = QFontMetrics(QCoreApplication.instance().font()).height()

        Logger.log('d', 'Using a line height of %s', self._line_height)

    themeLoaded = pyqtSignal()

    @pyqtProperty(QObject, notify = themeLoaded)
    def styles(self):
        return self._styles

    @pyqtSlot(str, result = str)
    def getIcon(self, name):
        svg = os.path.join(self._path, "icons", name + ".svg")
        if os.path.isfile(svg):
            return svg

        png = os.path.join(self._path, "icons", name + ".png")
        if os.path.isfile(png):
            return png

        Logger.log('e', "Icon {0} not found in theme".format(name))
        return Resources.getPath(Resources.ImagesLocation, 'checkerboard.png')

    @pyqtSlot(str, result = str)
    def getImage(self, name):
        png = os.path.join(self._path, "images", name + ".png")
        if os.path.isfile(png):
            return png

        Logger.log('e', "Image {0} not found in theme".format(name))
        return Resources.getPath(Resources.ImagesLocation, 'checkerboard.png')

    @pyqtProperty('QVariantMap', notify = themeLoaded)
    def colors(self):
        return self._colors

    @pyqtProperty('QVariantMap', notify = themeLoaded)
    def fonts(self):
        return self._fonts

    @pyqtProperty('QVariantMap', notify = themeLoaded)
    def sizes(self):
        return self._sizes

    @pyqtSlot(QUrl)
    def load(self, path):
        self._path = path.toLocalFile()

        with open(os.path.join(self._path, 'theme.json')) as f:
            data = json.load(f)

        self._fonts = {}
        self._colors = {}
        self._sizes = {}

        if 'colors' in data:
            for name, color in data['colors'].items():
                c = QColor(color[0], color[1], color[2], color[3])
                self._colors[name] = c

        if 'fonts' in data:
            for name, font in data['fonts'].items():
                f = QFont()

                f.setFamily(font.get('family', ''))
                f.setBold(font.get('bold', False))
                f.setItalic(font.get('italic', False))
                f.setPixelSize(font.get('size', 1) * self._line_height)

                self._fonts[name] = f

        if 'sizes' in data:
            for name, size in data['sizes'].items():
                s = QSizeF()
                s.setWidth(size[0] * self._line_height)
                s.setHeight(size[1] * self._line_height)

                self._sizes[name] = s

        styles = os.path.join(self._path, 'styles.qml')
        if os.path.isfile(styles):
            c = QQmlComponent(self._engine, styles)
            self._styles = c.create()

        Logger.log('d', 'Loaded theme %s', self._path)
        self.themeLoaded.emit()

def createTheme(engine, script_engine):
    return Theme(engine)

