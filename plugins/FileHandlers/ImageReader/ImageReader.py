# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import numpy
import math

from PyQt5.QtGui import QImage, qRed, qGreen, qBlue
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtQml import QQmlComponent, QQmlContext

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshReader import MeshReader
from UM.Mesh.MeshData import MeshData
from UM.Scene.SceneNode import SceneNode
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Logger import Logger
from UM.Job import Job

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")


class ImageReaderUI(QObject):
    show_config_ui_trigger = pyqtSignal()

    def __init__(self, image_reader):
        super(ImageReaderUI, self).__init__()
        self.image_reader = image_reader
        self.ui_view = None
        self.show_config_ui_trigger.connect(self._actualShowConfigUI)
        self.size = 120
        self.base_height = 2
        self.peak_height = 12
        self.smoothing = 1

    def showConfigUI(self):
        self.show_config_ui_trigger.emit()

    def _actualShowConfigUI(self):
        if self.ui_view is None:
            self._createConfigUI()
        self.ui_view.show()

    def _createConfigUI(self):
        if self.ui_view is None:
            Logger.log("d", "Creating ImageReader config UI")
            path = QUrl.fromLocalFile(os.path.join(PluginRegistry.getInstance().getPluginPath("ImageReader"), "ConfigUI.qml"))
            component = QQmlComponent(Application.getInstance()._engine, path)
            self.ui_context = QQmlContext(Application.getInstance()._engine.rootContext())
            self.ui_context.setContextProperty("manager", self)
            self.ui_view = component.create(self.ui_context)

            self.ui_view.setFlags(self.ui_view.flags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMinimizeButtonHint & ~Qt.WindowMaximizeButtonHint);

    @pyqtSlot()
    def onOkButtonClicked(self):
        self.image_reader.canceled = False
        self.image_reader.wait = False
        self.ui_view.close()

    @pyqtSlot()
    def onCancelButtonClicked(self):
        self.image_reader.canceled = True
        self.image_reader.wait = False
        self.ui_view.close()

    @pyqtSlot(str)
    def onSizeChanged(self, value):
        if (len(value) > 0):
            self.size = float(value)
        else:
            self.size = 0

    @pyqtSlot(str)
    def onBaseHeightChanged(self, value):
        if (len(value) > 0):
            self.base_height = float(value)
        else:
            self.base_height = 0

    @pyqtSlot(str)
    def onPeakHeightChanged(self, value):
        if (len(value) > 0):
            self.peak_height = float(value)
        else:
            self.peak_height = 0

    @pyqtSlot(str)
    def onSmoothingChanged(self, value):
        if (len(value) > 0):
            self.smoothing = int(value)
        else:
            self.smoothing = 0


class ImageReader(MeshReader):
    def __init__(self):
        super(ImageReader, self).__init__()
        self._supported_extensions = [".jpg", ".jpeg", ".bmp", ".gif", ".png"]
        self.ui = ImageReaderUI(self)
        self.wait = False
        self.canceled = False

    def blur(self, height_data):
        width = height_data.shape[0]
        height = height_data.shape[1]

        temp_data = numpy.copy(height_data)

        for x in range(0, width):
            for y in range(0, height):
                value = temp_data[x,y]
                div = 1

                if x < width-1:
                    value += temp_data[x+1,y]
                    div += 1
                if x > 0:
                    value += temp_data[x-1,y]
                    div += 1

                if y < height-1:
                    value += temp_data[x,y+1]
                    div += 1
                if y > 0:
                    value += temp_data[x,y-1]
                    div += 1

                value /= div
                height_data[x,y] = value

    def transformPoints(self, points, matrix):
        for i in range(0, len(points)):
            points[i] = points[i].preMultiply(matrix)

    def addQuad(self, mesh, matrix):
        points = [Vector(0,0,0), Vector(0,0,1), Vector(1,0,1), Vector(1,0,0)]
        self.transformPoints(points, matrix)
        mesh.addFace(points[0].x,points[0].y,points[0].z, points[1].x,points[1].y,points[1].z, points[2].x,points[2].y,points[2].z)
        mesh.addFace(points[2].x,points[2].y,points[2].z, points[3].x,points[3].y,points[3].z, points[0].x,points[0].y,points[0].z)

    def read(self, file_name):
        extension = os.path.splitext(file_name)[1]
        if extension.lower() in self._supported_extensions:
            self.ui.showConfigUI()
            self.wait = True
            self.canceled = True

            while self.wait:
                pass
                #this causes the config window to not repaint...
                #Job.yieldThread()

            result = None
            if not self.canceled:
                result = self.actualRead(file_name, self.ui.size, self.ui.peak_height, self.ui.base_height, self.ui.smoothing)

            return result

        return None

    def actualRead(self, file_name, xz_size, peak_height, base_height, blur_iterations):
        mesh = None
        scene_node = None
        
        scene_node = SceneNode()

        mesh = MeshData()
        scene_node.setMeshData(mesh)
        
        img = QImage(file_name)
        width = max(img.width(), 2)
        height = max(img.height(), 2)
        aspect = height/width

        if img.width() < 2 or img.height() < 2:
            img = img.scaled(width, height, Qt.IgnoreAspectRatio)

        base_height = max(base_height, 0)

        xz_size = max(xz_size, 1)
        scale_vector = Vector(xz_size, max(peak_height-base_height, -base_height), xz_size)

        if width > height:
            scale_vector.setZ(scale_vector.z*aspect)
        elif height > width:
            scale_vector.setX(scale_vector.x/aspect)

        if width > 512 or height > 512:
            scale_factor = 512/width
            if height > width:
                scale_factor = 512/height

            width = int(max(round(width*scale_factor), 2))
            height = int(max(round(height*scale_factor), 2))
            img = img.scaled(width, height, Qt.IgnoreAspectRatio)

        Job.yieldThread()

        height_data = numpy.empty((width, height), dtype=numpy.float32)

        for x in range(0, width):
            for y in range(0, height):
                qrgb = img.pixel(x, y)
                avg = float(qRed(qrgb)+qGreen(qrgb)+qBlue(qrgb))/(3*255)
                height_data[x, y] = avg

        Job.yieldThread()

        for i in range(0, blur_iterations):
            self.blur(height_data)
            Job.yieldThread()

        texel_width = 1.0/(width-1)*scale_vector.x
        texel_height = 1.0/(height-1)*scale_vector.z

        mesh.reserveFaceCount(2*height*width+2*5)

        print("Start mesh build")

        for x in range(0, width-1):
            for y in range(0, height-1):
                h00 = height_data[x, y]
                h01 = height_data[x, y+1]
                h11 = height_data[x+1, y+1]
                h10 = height_data[x+1, y]

                #edge vertices must be 0 on y
                if x <= 0:
                    h00 = 0
                    h01 = 0
                if x >= width-2:
                    h11 = 0
                    h10 = 0
                if y <= 0:
                    h00 = 0
                    h10 = 0
                if y >= height-2:
                    h01 = 0
                    h11 = 0

                offset_x = texel_width*x
                offset_y = base_height
                offset_z = texel_height*y

                v00x = offset_x+0
                v00y = offset_y+h00*scale_vector.y
                v00z = offset_z+0

                v01x = offset_x+0
                v01y = offset_y+h01*scale_vector.y
                v01z = offset_z+texel_height

                v11x = offset_x+texel_width
                v11y = offset_y+h11*scale_vector.y
                v11z = offset_z+texel_height

                v10x = offset_x+texel_width
                v10y = offset_y+h10*scale_vector.y
                v10z = offset_z+0

                mesh.addFace(v00x,v00y,v00z, v01x,v01y,v01z, v11x,v11y,v11z)
                mesh.addFace(v11x,v11y,v11z, v10x,v10y,v10z, v00x,v00y,v00z)

            Job.yieldThread()

        mat = Matrix()

        #bottom
        mat.setByTranslation(Vector(0, 0, 0))
        mat.scaleByFactor(scale_vector.x, direction = Vector(1,0,0))
        mat.scaleByFactor(scale_vector.z, direction = Vector(0,0,1))
        self.addQuad(mesh, mat)

        #west
        mat.setByTranslation(Vector(0, 0, 0))
        mat.rotateByAxis(math.pi*0.5, Vector(0,0,1))
        mat.scaleByFactor(base_height, direction = Vector(1,0,0))
        mat.scaleByFactor(scale_vector.z, direction = Vector(0,0,1))
        self.addQuad(mesh, mat)

        #east
        mat.setByTranslation(Vector(scale_vector.x, base_height, 0))
        mat.rotateByAxis(math.pi*-0.5, Vector(0,0,1))
        mat.scaleByFactor(base_height, direction = Vector(1,0,0))
        mat.scaleByFactor(scale_vector.z, direction = Vector(0,0,1))
        self.addQuad(mesh, mat)

        #north
        mat.setByTranslation(Vector(0, base_height, 0))
        mat.rotateByAxis(math.pi*0.5, Vector(0,1,0))
        mat.rotateByAxis(-math.pi*0.5, Vector(0,0,1))
        mat.scaleByFactor(base_height, direction = Vector(1,0,0))
        mat.scaleByFactor(scale_vector.x, direction = Vector(0,0,1))
        self.addQuad(mesh, mat)

        #south
        mat.setByTranslation(Vector(0, 0, scale_vector.z))
        mat.rotateByAxis(math.pi*0.5, Vector(0,1,0))
        mat.rotateByAxis(math.pi*0.5, Vector(0,0,1))
        mat.scaleByFactor(base_height, direction = Vector(1,0,0))
        mat.scaleByFactor(scale_vector.x, direction = Vector(0,0,1))
        self.addQuad(mesh, mat)

        mesh.calculateNormals(fast = True)

        return scene_node

