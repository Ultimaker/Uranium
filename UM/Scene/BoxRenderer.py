# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Vector import Vector
from UM.Scene.ToolHandle import ToolHandle

class BoxRenderer(ToolHandle):
    def __init__(self, box, parent = None):
        super().__init__(parent)

        md = self.getMeshData()

        rtf = box.maximum
        lbb = box.minimum

        md.addVertex(rtf.x, rtf.y, rtf.z) #Right - Top - Front
        md.addVertex(lbb.x, rtf.y, rtf.z) #Left - Top - Front

        md.addVertex(lbb.x, rtf.y, rtf.z) #Left - Top - Front
        md.addVertex(lbb.x, lbb.y, rtf.z) #Left - Bottom - Front

        md.addVertex(lbb.x, lbb.y, rtf.z) #Left - Bottom - Front
        md.addVertex(rtf.x, lbb.y, rtf.z) #Right - Bottom - Front

        md.addVertex(rtf.x, lbb.y, rtf.z) #Right - Bottom - Front
        md.addVertex(rtf.x, rtf.y, rtf.z) #Right - Top - Front

        md.addVertex(rtf.x, rtf.y, lbb.z) #Right - Top - Back
        md.addVertex(lbb.x, rtf.y, lbb.z) #Left - Top - Back

        md.addVertex(lbb.x, rtf.y, lbb.z) #Left - Top - Back
        md.addVertex(lbb.x, lbb.y, lbb.z) #Left - Bottom - Back

        md.addVertex(lbb.x, lbb.y, lbb.z) #Left - Bottom - Back
        md.addVertex(rtf.x, lbb.y, lbb.z) #Right - Bottom - Back

        md.addVertex(rtf.x, lbb.y, lbb.z) #Right - Bottom - Back
        md.addVertex(rtf.x, rtf.y, lbb.z) #Right - Top - Back

        md.addVertex(rtf.x, rtf.y, rtf.z) #Right - Top - Front
        md.addVertex(rtf.x, rtf.y, lbb.z) #Right - Top - Back

        md.addVertex(lbb.x, rtf.y, rtf.z) #Left - Top - Front
        md.addVertex(lbb.x, rtf.y, lbb.z) #Left - Top - Back

        md.addVertex(lbb.x, lbb.y, rtf.z) #Left - Bottom - Front
        md.addVertex(lbb.x, lbb.y, lbb.z) #Left - Bottom - Back

        md.addVertex(rtf.x, lbb.y, rtf.z) #Right - Bottom - Front
        md.addVertex(rtf.x, lbb.y, lbb.z) #Right - Bottom - Back
