# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QUrl, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtQuick import QQuickPaintedItem
from PyQt6.QtSvg import QSvgRenderer
from UM.Application import Application
from UM.Logger import Logger


# This is meant as a potential replacement for RecolorImage.
# As we had issues with upgrading to qt6 on windows with the shader, this was developed as an alternative
class ColorImage(QQuickPaintedItem):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._source = QUrl()
        self._color = QColor()
        self._svg_data = b""
        self._renderer = None

    sourceChanged = pyqtSignal()
    colorChanged = pyqtSignal()

    def _updateSVG(self) -> None:
        if not self._source or self._source.toLocalFile() == "":
            return
        try:
            with open(self._source.toLocalFile(), "rb") as f:
                self._svg_data = f.read()
        except FileNotFoundError:
            Logger.log("w", f"Unable to find image located at {self._source.toLocalFile()}")
            return
        self._svg_data = self._svg_data.replace(b"<svg ", b"<svg fill=\"%s\" " % self._color.name().encode("utf-8"))
        self._renderer = QSvgRenderer(self._svg_data)
        self.update()

    def setSource(self, source: QUrl) -> None:
        if self._source != source:
            self._source = source
            self.sourceChanged.emit()
            self._updateSVG()

    @pyqtProperty(QUrl, fset = setSource, notify = sourceChanged)
    def source(self) -> QUrl:
        return self._source

    def setColor(self, color: QColor) -> None:
        if self._color != color:
            self._color = color
            self.colorChanged.emit()
            self._updateSVG()

    @pyqtProperty(QColor, fset = setColor, notify = colorChanged)
    def color(self) -> QColor:
        return self._color

    def paint(self, painter: QPainter) -> None:
        pixel_ratio = Application.getInstance().getMainWindow().effectiveDevicePixelRatio()
        painter.scale(1 / pixel_ratio, 1 / pixel_ratio)
        if self._renderer:
            self._renderer.render(painter)
