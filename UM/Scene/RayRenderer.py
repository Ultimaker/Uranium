from UM.Scene.ToolHandle import ToolHandle

class RayRenderer(ToolHandle):
    def __init__(self, ray, parent = None):
        super().__init__(parent)

        md = self.getMeshData()

        md.addVertex(0, 0, 0)
        md.addVertex(ray.direction.x * 500, ray.direction.y * 500, ray.direction.z * 500)

        self.setPosition(ray.origin)
