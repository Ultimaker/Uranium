
from typing import Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from UM.Scene.SceneNode import SceneNode


class MeshManager:

    def __init__(self, application):
        super().__init__()
        self._application = application
        self._mesh_read_finished_callbacks = []

    def add_mesh_read_finished_callback(self, func: Callable[[str, List["SceneNode"]], List["SceneNode"]]) -> None:
        self._mesh_read_finished_callbacks.append(func)

    def invoke_mesh_read_finished_callbacks(self, file_name: str, nodes: List["SceneNode"]) -> List["SceneNode"]:
        for func in self._mesh_read_finished_callbacks:
            nodes = func(file_name, nodes)

        return nodes
