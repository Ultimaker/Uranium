from UM.View.View import View
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Resources import Resources
from UM.Application import Application
from UM.Math.Color import Color

import math

class MeshView(View):
    def __init__(self):
        super().__init__()
        self._material = None

    def beginRendering(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        if not self._material:
            self._material = renderer.createMaterial(Resources.getPath(Resources.ShadersLocation, 'default.vert'), Resources.getPath(Resources.ShadersLocation, 'default.frag'))

            self._material.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
            self._material.setUniformValue("u_diffuseColor", Color(1.0, 0.79, 0.14, 1.0))
            self._material.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
            self._material.setUniformValue('u_overhangColor', Color(1.0, 0.0, 0.0, 1.0))
            self._material.setUniformValue("u_shininess", 50.0)

        if Application.getInstance().getActiveMachine():
            angle = Application.getInstance().getActiveMachine().getSettingValueByKey('support_angle')
            if angle != None:
                self._material.setUniformValue('u_overhangAngle', math.cos(math.radians(90 - angle)))

        for node in DepthFirstIterator(scene.getRoot()):
            if not node.render(renderer):
                if node.getMeshData() and node.isVisible():
                    renderer.queueNode(node, material = self._material)

    def endRendering(self):
        pass
