from UM.Scene.ToolHandle import ToolHandle

class ScaleToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        md = self.getMeshData()

        md.addVertex(0, 0, 0)
        md.addVertex(0, 20, 0)
        md.addVertex(0, 0, 0)
        md.addVertex(20, 0, 0)
        md.addVertex(0, 0, 0)
        md.addVertex(0, 0, 20)
