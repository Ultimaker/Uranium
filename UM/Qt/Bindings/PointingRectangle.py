# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import pyqtProperty, pyqtSignal
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtQuick import QQuickItem, QSGGeometryNode, QSGGeometry, QSGFlatColorMaterial


class PointingRectangle(QQuickItem):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setFlag(QQuickItem.ItemHasContents)

        self._arrow_size = 0
        self._color = QColor(255, 255, 255, 255)
        self._target = QPoint(0,0)
        self._border_width = 0
        self._border_color = QColor(0, 0, 0, 255)

        self._geometry = None
        self._material = None
        self._node = None
        self._border_geometry = None
        self._border_material = None
        self._border_node = None

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
    color = pyqtProperty(QColor, fget=getColor, fset=setColor, notify=colorChanged)

    def getBorderWidth(self):
        return self._border_width

    def setBorderWidth(self, size):
        if size != self._border_width:
            self._border_width = size
            self.update()
            self.borderWidthChanged.emit()

    borderWidthChanged = pyqtSignal()
    borderWidth = pyqtProperty(float, fget=getBorderWidth, fset=setBorderWidth, notify=borderWidthChanged)

    def getBorderColor(self):
        return self._border_color

    def setBorderColor(self, color):
        if color != self._border_color:
            self._border_color = color
            self.update()
            self.borderColorChanged.emit()

    borderColorChanged = pyqtSignal()
    borderColor = pyqtProperty(QColor, fget=getBorderColor, fset=setBorderColor, notify=borderColorChanged)

    def updatePaintNode(self, paint_node, update_data):
        if paint_node is None:
            paint_node = QSGGeometryNode()

        geometry = QSGGeometry(QSGGeometry.defaultAttributes_Point2D(), 7, 9)
        geometry.setDrawingMode(QSGGeometry.GL_TRIANGLES)
        vertex_data = geometry.vertexDataAsPoint2D()
        vertex_data[0].set(0, 0)
        vertex_data[1].set(0, self.height())
        vertex_data[2].set(self.width(), self.height())
        vertex_data[3].set(self.width(), 0)

        # no arrow by default
        vertex_data[4].set(0, 0)
        vertex_data[5].set(0, 0)
        vertex_data[6].set(0, 0)

        target_offset = self._target - QPoint(self.x(), self.y())

        arrow_on_side = -1 # no arrow
        arrow_size = 0
        arrow_offset = 0

        if target_offset.x() >= 0 and target_offset.x() <= self.width():
            arrow_size = min(self._arrow_size, self.width()/2)
            arrow_offset = max(arrow_size, min(self.width() - arrow_size, target_offset.x()))
            if target_offset.y() < 0:
                # top
                vertex_data[4].set(arrow_offset - arrow_size, 0)
                vertex_data[5].set(arrow_offset, - arrow_size)
                vertex_data[6].set(arrow_offset + arrow_size, 0)
                arrow_on_side = 0
            elif target_offset.y() > self.height():
                # bottom
                vertex_data[4].set(arrow_offset - arrow_size, self.height())
                vertex_data[5].set(arrow_offset, self.height() +arrow_size)
                vertex_data[6].set(arrow_offset + arrow_size, self.height())
                arrow_on_side = 2
        elif target_offset.y() >= 0 and target_offset.y() <= self.height():
            arrow_size = min(self._arrow_size, self.height()/2)
            arrow_offset = max(arrow_size, min(self.height() - arrow_size, target_offset.y()))
            if target_offset.x() < 0:
                # left
                vertex_data[4].set(0, arrow_offset - arrow_size)
                vertex_data[5].set(-arrow_size, arrow_offset)
                vertex_data[6].set(0, arrow_offset + arrow_size)
                arrow_on_side = 3
            elif target_offset.x() > self.width():
                # right
                vertex_data[4].set(self.width(), arrow_offset - arrow_size)
                vertex_data[5].set(self.width() + arrow_size, arrow_offset)
                vertex_data[6].set(self.width(), arrow_offset + arrow_size)
                arrow_on_side = 1

        index_data = geometry.indexDataAsUShort()
        index_data[0] = 0
        index_data[1] = 1
        index_data[2] = 2

        index_data[3] = 0
        index_data[4] = 2
        index_data[5] = 3

        index_data[6] = 4
        index_data[7] = 5
        index_data[8] = 6

        paint_node.setGeometry(geometry)

        material = QSGFlatColorMaterial()
        material.setColor(self._color)

        paint_node.setMaterial(material)

        if self._border_width > 0:
            if paint_node.childCount() == 0:
                border_node = QSGGeometryNode()
            else:
                border_node = paint_node.firstChild()

            border_vertices = []
            border_vertices.append((0, 0))
            if arrow_on_side == 0:
                border_vertices.append((arrow_offset - arrow_size, 0))
                border_vertices.append((arrow_offset, - arrow_size))
                border_vertices.append((arrow_offset + arrow_size, 0))
            border_vertices.append((self.width(), 0))
            if arrow_on_side == 1:
                border_vertices.append((self.width(), arrow_offset - arrow_size))
                border_vertices.append((self.width() + arrow_size, arrow_offset))
                border_vertices.append((self.width(), arrow_offset + arrow_size))
            border_vertices.append((self.width(), self.height()))
            if arrow_on_side == 2:
                border_vertices.append((arrow_offset + arrow_size, self.height()))
                border_vertices.append((arrow_offset, self.height() + arrow_size))
                border_vertices.append((arrow_offset - arrow_size, self.height()))
            border_vertices.append((0,self.height()))
            if arrow_on_side == 3:
                border_vertices.append((0, arrow_offset + arrow_size))
                border_vertices.append((- arrow_size, arrow_offset))
                border_vertices.append((0, arrow_offset - arrow_size))

            border_geometry = QSGGeometry(QSGGeometry.defaultAttributes_Point2D(), 2 * len(border_vertices), 0)
            border_geometry.setDrawingMode(QSGGeometry.GL_LINES)
            border_geometry.setLineWidth(self._border_width)

            border_vertex_data = border_geometry.vertexDataAsPoint2D()
            for index in range(len(border_vertices)):
                start_vertex = border_vertices[index]
                end_vertex = border_vertices[index + 1] if index < len(border_vertices) -1 else border_vertices[0]
                border_vertex_data[2 * index].set(start_vertex[0], start_vertex[1])
                border_vertex_data[2 * index + 1].set(end_vertex[0], end_vertex[1])

            border_node.setGeometry(border_geometry)

            border_material = QSGFlatColorMaterial()
            border_material.setColor(self._border_color)

            border_node.setMaterial(border_material)

            if paint_node.childCount() == 0:
                paint_node.appendChildNode(border_node)
        else:
            border_node = None
            border_geometry = None
            border_material = None
            paint_node.removeAllChildNodes()

        # For PyQt 5.4, I need to store these otherwise they will be garbage collected before rendering
        # and never show up, but otherwise never crash.
        self._node = paint_node
        self._geometry = geometry
        self._material = material
        self._border_node = border_node
        self._border_geometry = border_geometry
        self._border_material = border_material

        return paint_node
