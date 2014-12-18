from UM.Scene.ToolHandle import ToolHandle

class TranslateToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        md = self.getMeshData()

        md.addVertex(0, 0, 0)
        md.addVertex(0, 20, 0)

        md.addVertex(0, 20, 0)
        md.addVertex(2, 18, 0)
        md.addVertex(0, 20, 0)
        md.addVertex(-2, 18, 0)

        md.addVertex(0, 0, 0)
        md.addVertex(20, 0, 0)

        md.addVertex(20, 0, 0)
        md.addVertex(18, 2, 0)
        md.addVertex(20, 0, 0)
        md.addVertex(18, -2, 0)

        md.addVertex(0, 0, 0)
        md.addVertex(0, 0, 20)

        md.addVertex(0, 0, 20)
        md.addVertex(0, 2, 18)
        md.addVertex(0, 0, 20)
        md.addVertex(0, -2, 18)
