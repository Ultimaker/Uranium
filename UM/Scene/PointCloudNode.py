# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import SceneNode
from UM.Application import Application
from UM.Resources import Resources
from UM.Math.Color import Color
from UM.ColorGenerator import ColorGenerator
from UM.View.GL.OpenGL import OpenGL
from UM.View.RenderBatch import RenderBatch
import numpy
import colorsys


class PointCloudNode(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = "Pointcloud"
        self._selectable = True
        Application.getInstance().addCloudNode(self)
        self._material = None
        self._color = Color(0,0,0,1)
        if parent:
            self._onParentChanged(parent)
        
        self.parentChanged.connect(self._onParentChanged)
    
    def _onParentChanged(self, parent):
        num_scans = 12 #Hardcoded, change this!
        if parent.callDecoration("isGroup"):
            if not hasattr(parent, "color"):
                Application.getInstance().addColorIndex(parent)
                color_hsv = ColorGenerator().getColor(Application.getInstance().getColorIndex(parent))
                #r,g,b = colorsys.hsv_to_rgb(color_hsv[0], color_hsv[1], color_hsv[2])
                setattr(parent, "color", color_hsv)
            color_hsv = getattr(parent, "color")
            if len(parent.getChildren()) > num_scans * 0.5:
                color_hsv[1] = 0.4 + (0.6 / ((num_scans * 0.5) - 1) * (len(parent.getChildren()) - 1. - 0.5 * num_scans))
            else: 
                color_hsv[1] = 1. - (0.6 / ((num_scans * 0.5) - 1)  * (len(parent.getChildren()) - 1.))
            
            r,g,b = colorsys.hsv_to_rgb(color_hsv[0], color_hsv[1], color_hsv[2])
            self.setColor(Color(r,g,b,1))
        else:
            Application.getInstance().addColorIndex(self)
            color_hsv = ColorGenerator().getColor(Application.getInstance().getColorIndex(self))
            r,g,b = colorsys.hsv_to_rgb(color_hsv[0], color_hsv[1], color_hsv[2])
            self.setColor(Color(r,g,b,1))
   
    def getColor(self):
        return self._color
    
    def setColor(self, color):
        self._color = color
        self._material = None # Reset material 
    
    ##   \brief Create new material. 
    def createMaterial(self):
        self._material = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "object.shader"))

        self._material.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
        self._material.setUniformValue("u_diffuseColor", self._color)
        self._material.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
        self._material.setUniformValue("u_shininess", 50.0)
    
    def render(self, renderer):
        if not self._material:
            self.createMaterial()
        if self.getMeshData() and self.isVisible():
            renderer.queueNode(self, mode = RenderBatch.RenderMode.Points, shader = self._material)
            return True
    
    ##  \brief Set the mesh of this node/object
    #   \param mesh_data MeshData object
    def setMeshData(self, mesh_data):
        id = Application.getInstance().getCloudNodeIndex(self)
        
        # Create a unique color for each vert. First 3 uint 8  represent index in this cloud, final uint8 gives cloud ID.
        vertice_indices = numpy.arange(mesh_data.getVertexCount(), dtype = numpy.int32)
        cloud_indices = numpy.empty(mesh_data.getVertexCount(), dtype = numpy.int32)
        cloud_indices.fill(255 - id)
        cloud_indices  = numpy.left_shift(cloud_indices, 24) # shift 24 bits.
        combined_clouds = numpy.add(cloud_indices,vertice_indices)
        data = numpy.fromstring(combined_clouds.tostring(),numpy.uint8)

        colors = numpy.resize(data,(mesh_data.getVertexCount(), 4))
        colors = colors.astype(numpy.float32)
        colors /= 255
        self._mesh_data = mesh_data.set(colors=colors)
        self._resetAABB()
        self.meshDataChanged.emit(self)
