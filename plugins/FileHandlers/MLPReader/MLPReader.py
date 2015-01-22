from UM.WorkspaceReader import WorkspaceReader

class MLPReader(WorkspaceReader):
    def __init__(self):
        super().__init__()
        self._supported_extension = ".mlp"
    
    def read(self, file_name, storage_device): 
        pass
        