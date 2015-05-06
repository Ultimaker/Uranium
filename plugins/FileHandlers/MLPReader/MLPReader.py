# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.WorkspaceReader import WorkspaceReader
from UM.Scene.SceneNode import SceneNode
from UM.Scene.PointCloudNode import PointCloudNode
from UM.Logger import Logger
import xml.etree.ElementTree as ET
from UM.Application import Application
from UM.Mesh.MeshData import MeshType
from UM.Math.Matrix import Matrix

import os

class MLPReader(WorkspaceReader):
    def __init__(self):
        super().__init__()
        self._supported_extension = ".mlp"
    
    def read(self, file_name, storage_device): 
        extension = os.path.splitext(file_name)[1]
        if extension.lower() == self._supported_extension:
            loaded_workspace = SceneNode()
            mesh_handler = Application.getInstance().getMeshFileHandler()
            f = storage_device.openFile(file_name, "rt")
            
            tree = ET.parse(f)
            root = tree.getroot()
            if root.tag == "MeshLabProject":
                for group in root.findall("MeshGroup"):
                    for mesh in group.findall("MLMesh"): 
                        mesh_data = mesh_handler.read(mesh.get("filename"),Application.getInstance().getStorageDevice("local"))
                        mesh_data.setName(mesh.get("label"))
                        if mesh_data.getType() is MeshType.pointcloud:
                            mesh_node = PointCloudNode(loaded_workspace)
                        else:
                            mesh_node = SceneNode(loaded_workspace)
                        mesh_lines = mesh.findall("MLMatrix44")[0].text.splitlines()
                        mesh_matrix = Matrix()
                        mesh_matrix.setColumn(0,mesh_lines[1].split())
                        mesh_matrix.setColumn(1,mesh_lines[2].split())
                        mesh_matrix.setColumn(2,mesh_lines[3].split())
                        mesh_matrix.setColumn(3,mesh_lines[4].split())
                        mesh_node.setMeshData(mesh_data)
                return loaded_workspace
            else:
                Logger.log("e", "Unable to load file. It seems to be formated wrong.")
                return None
        else:
            return None # Can't do anything with provided extention
