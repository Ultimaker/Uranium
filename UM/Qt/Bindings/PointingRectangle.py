# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, PYQT_VERSION
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtQuick import QQuickItem, QSGGeometryNode, QSGGeometry, QSGFlatColorMaterial, QSGSimpleRectNode

class PointingRectangle(QQuickItem):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setFlag(QQuickItem.ItemHasContents)

        self._arrow_size = 0
        self._color = QColor(255, 255, 255, 255)
        self._target = QPoint(0,0)

        self._geometry = None
        self._material = None
        self._node = None
        self._attributes = None

    def getArrowSize(self):
        return self._arrow_size

    def setArrowSize(self, size):
        if size != self._arrow_size:
            self._arrow_size = size
            self.update()
            self.arrowSizeChanged.emit()

    arrowSizeChanged = pyqtSignal()
    arrowSize = pyqtProperty(float, fget=getArrowSize, fset=setArrowSize, notify=arrowSizeChanged)

    def getTarget(self):
        return self._target

    def setTarget(self, target):
        if target != self._target:
            self._target = target
            self.update()
            self.targetChanged.emit()

    targetChanged = pyqtSignal()
    target = pyqtProperty(QPoint, fget=getTarget, fset=setTarget, notify=targetChanged)

    def getColor(self):
        return self._color

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.update()
            self.colorChanged.emit()

    colorChanged = pyqtSignal()

    colorChanged = pyqtSignal()
    color = pyqtProperty(QColor, fget=getColor, fset=setColor, notify=colorChanged)

    def updatePaintNode(self, paint_node, update_data):
        if paint_node is None:
            paint_node = QSGGeometryNode()

        geometry = QSGGeometry(QSGGeometry.defaultAttributes_Point2D(), 7, 9)
        geometry.setDrawingMode(QSGGeometry.GL_TRIANGLES)
        geometry.vertexDataAsPoint2D()[0].set(0, 0)
        geometry.vertexDataAsPoint2D()[1].set(0, self.height())
        geometry.vertexDataAsPoint2D()[2].set(self.width(), self.height())
        geometry.vertexDataAsPoint2D()[3].set(self.width(), 0)
        
        # no arrow by default
        geometry.vertexDataAsPoint2D()[4].set(0, 0)
        geometry.vertexDataAsPoint2D()[5].set(0, 0)
        geometry.vertexDataAsPoint2D()[6].set(0, 0)

        target_offset = self._target - QPoint(self.x(), self.y())

        if target_offset.x() >= 0 and target_offset.x() <= self.width():
            arrow_size = min(self._arrow_size, self.width()/2)
            arrow_offset = max(arrow_size, min(self.width() - arrow_size, target_offset.x()))
            if target_offset.y() < 0:
                # top
                geometry.vertexDataAsPoint2D()[4].set(arrow_offset - arrow_size, 0)
                geometry.vertexDataAsPoint2D()[5].set(arrow_offset, - arrow_size)
                geometry.vertexDataAsPoint2D()[6].set(arrow_offset + arrow_size, 0)
            elif target_offset.y() > self.height():
                # bottom
                geometry.vertexDataAsPoint2D()[4].set(arrow_offset - arrow_size, self.height())
                geometry.vertexDataAsPoint2D()[5].set(arrow_offset, self.height() +arrow_size)
                geometry.vertexDataAsPoint2D()[6].set(arrow_offset + arrow_size, self.height())
        elif target_offset.y() >= 0 and target_offset.y() <= self.height():
            arrow_size = min(self._arrow_size, self.height()/2)
            arrow_offset = max(arrow_size, min(self.height() - arrow_size, target_offset.y()))
            if target_offset.x() < 0:
                # left
                geometry.vertexDataAsPoint2D()[4].set(0, arrow_offset - arrow_size)
                geometry.vertexDataAsPoint2D()[5].set(-arrow_size, arrow_offset)
                geometry.vertexDataAsPoint2D()[6].set(0, arrow_offset + arrow_size)
            elif target_offset.x() > self.width():
                # right
                geometry.vertexDataAsPoint2D()[4].set(self.width(), arrow_offset - arrow_size)
                geometry.vertexDataAsPoint2D()[5].set(self.width() + arrow_size, arrow_offset)
                geometry.vertexDataAsPoint2D()[6].set(self.width(), arrow_offset + arrow_size)
                
        geometry.indexDataAsUShort()[0] = 0
        geometry.indexDataAsUShort()[1] = 1
        geometry.indexDataAsUShort()[2] = 2

        geometry.indexDataAsUShort()[3] = 0
        geometry.indexDataAsUShort()[4] = 2
        geometry.indexDataAsUShort()[5] = 3

        geometry.indexDataAsUShort()[6] = 4
        geometry.indexDataAsUShort()[7] = 5
        geometry.indexDataAsUShort()[8] = 6

        paint_node.setGeometry(geometry)

        material = QSGFlatColorMaterial()
        material.setColor(self._color)

        paint_node.setMaterial(material)

        # For PyQt 5.4, I need to store these otherwise they will be garbage collected before rendering
        # and never show up, but otherwise never crash.
        self._paint_node = paint_node
        self._geometry = geometry
        self._material = material

        return paint_node
