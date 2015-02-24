from UM.WorkspaceWriter import WorkspaceWriter
import xml.etree.ElementTree as ET

class MLPWriter(WorkspaceWriter):
    def __init__(self):
        super().__init__()
        self._supported_extension = ".mlp"
    
    def write(self, file_name, storage_device):
        '''if(self._supported_extension in file_name):
            f = storage_device.openFile(file_name, 'wb')
            mesh_lab_project = ET.Element("MeshLabProject")
            mesh_group = ET.SubElement(mesh_lab_project,"MeshGroup")
            mesh = ET.SubElement(mesh_group, "MLMesh", {"label":"test","filename":"test.ply"})
            matrix = ET.SubElement(mesh,"MLMatrix44")
            matrix.text = "1 0 0 0 \n 0 1 0 0 \n 0 0 1 0 \n 0 0 0 1"
            ET.dump(mesh_lab_project)'''
        return None