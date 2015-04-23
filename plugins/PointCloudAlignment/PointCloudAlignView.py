from UM.View.View import View
from UM.Resources import Resources
from UM.Math.Color import Color
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.PointCloudNode import PointCloudNode
from UM.View.Renderer import Renderer

class PointCloudAlignView(View):
    def __init__(self):
        super().__init__()
        self._active_material = None
        self._deactive_material = None
    
    def beginRendering(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()
        # Create two materials; an active material (normal) and a deactive material (slightly transparent)
        if not self._active_material:
            self._active_material = renderer.createMaterial(Resources.getPath(Resources.ShadersLocation, 'default.vert'), Resources.getPath(Resources.ShadersLocation, 'default.frag'))
            self._active_material.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
            self._active_material.setUniformValue("u_diffuseColor", Color(1.0, 0.79, 0.14, 1.0))
            self._active_material.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
            self._active_material.setUniformValue('u_overhangColor', Color(1.0, 0.0, 0.0, 1.0))
            self._active_material.setUniformValue("u_shininess", 50.0)
        if not self._deactive_material:
            self._deactive_material = renderer.createMaterial(Resources.getPath(Resources.ShadersLocation, 'default.vert'), Resources.getPath(Resources.ShadersLocation, 'default.frag'))
            self._deactive_material.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
            self._deactive_material.setUniformValue("u_diffuseColor", Color(0.1,0.1, 0.1,1))
            self._deactive_material.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
            self._deactive_material.setUniformValue('u_overhangColor', Color(1.0, 0.0, 0.0, 1.0))
            self._deactive_material.setUniformValue("u_shininess", 50.0)
        #print("starting iterator")    
        for node in DepthFirstIterator(scene.getRoot()):
            if type(node) == PointCloudNode:
                if node.getMeshData() and node.isVisible():
                    #print(node)
                    if node.isEnabled():      
                        renderer.queueNode(node, mode = Renderer.RenderPoints, material = self._active_material)
                    else:
                        renderer.queueNode(node, mode = Renderer.RenderPoints, material = self._deactive_material)
            else:
                node.render(renderer)

    def endRendering(self):
        pass