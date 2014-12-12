from Cura.Math.AxisAlignedBox import AxisAlignedBox
from Cura.Math.Vector import Vector
from Cura.Scene.ToolHandle import ToolHandle

class BoxRenderer(ToolHandle):
    def __init__(self, box, parent = None):
        super().__init__(parent)

        md = self.getMeshData()

        rtf = box.rightTopFront
        lbb = box.leftBottomBack

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
