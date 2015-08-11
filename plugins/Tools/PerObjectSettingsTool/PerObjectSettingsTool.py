# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.ScaleOperation import ScaleOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Application import Application

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import PerObjectSettingsToolHandle
from . import PerObjectSettingsModel

class PerObjectSettingsTool(Tool):
    def __init__(self):
        super().__init__()

        self._renderer = Application.getInstance().getRenderer()
        self._handle = PerObjectSettingsToolHandle.PerObjectSettingsToolHandle()
        self._model = PerObjectSettingsModel.PerObjectSettingsModel()

        self.setExposedProperties("Model")

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            self._handle.setParent(self.getController().getScene().getRoot())

        if event.type == Event.ToolDeactivateEvent:
            self._handle.setParent(None)

        if event.type == Event.MouseReleaseEvent:
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return False

            #if self.getLockedAxis():
                #op = None
                #if Selection.getCount() == 1:
                    #node = Selection.getSelectedObject(0)
                    #scale = node.getScale()
                    #if self.getLockedAxis() == ToolHandle.XAxis:
                        #scale.setX(-scale.x)
                    #elif self.getLockedAxis() == ToolHandle.YAxis:
                        #scale.setY(-scale.y)
                    #elif self.getLockedAxis() == ToolHandle.ZAxis:
                        #scale.setZ(-scale.z)

                    #op = ScaleOperation(node, scale, set_scale=True)
                #else:
                    #op = GroupedOperation()

                    #for node in Selection.getAllSelectedObjects():
                        #scale = node.getScale()
                        #if self.getLockedAxis() == ToolHandle.XAxis:
                            #scale.setX(-scale.x)
                        #elif self.getLockedAxis() == ToolHandle.YAxis:
                            #scale.setY(-scale.y)
                        #elif self.getLockedAxis() == ToolHandle.ZAxis:
                            #scale.setZ(-scale.z)

                        #op.addOperation(ScaleOperation(node, scale, set_scale = True))

                #op.push()

                #self.setLockedAxis(None)
                #return True

        return False

    def getModel(self):
        return self._model
