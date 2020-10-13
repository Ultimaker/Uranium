# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Union, List

import UM.Application
from UM.FileHandler.FileReader import FileReader
from UM.Scene.SceneNode import SceneNode


class MeshReader(FileReader):
    def __init__(self) -> None:
        super().__init__()

    def read(self, file_name: str) -> Union[SceneNode, List[SceneNode]]:
        """Read mesh data from file and returns a node that contains the data 
        Note that in some cases you can get an entire scene of nodes in this way (eg; 3MF)

        :return: node :type{SceneNode} or :type{list(SceneNode)} The SceneNode or SceneNodes read from file.
        """

        result = self._read(file_name)
        UM.Application.Application.getInstance().getController().getScene().addWatchedFile(file_name)
        return result

    def _read(self, file_name: str) -> Union[SceneNode, List[SceneNode]]:
        raise NotImplementedError("MeshReader plugin was not correctly implemented, no read was specified")
