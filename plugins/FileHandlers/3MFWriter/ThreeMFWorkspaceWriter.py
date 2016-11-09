from UM.Workspace.WorkspaceWriter import WorkspaceWriter
from UM.Application import Application
import zipfile


class ThreeMFWorkspaceWriter(WorkspaceWriter):
    def __init__(self):
        super().__init__()

    def write(self, stream, nodes, mode=WorkspaceWriter.OutputMode.BinaryMode):
        mesh_writer = Application.getInstance().getMeshFileHandler().getWriter("3MFWriter")

        if not mesh_writer:  # We need to have the 3mf mesh writer, otherwise we can't save the entire workspace
            return False

        # Indicate that the 3mf mesh writer should not close the archive just yet (we still need to add stuff to it).
        mesh_writer.setStoreArchive(True)
        mesh_writer.write(stream, nodes, mode)
        archive = mesh_writer.getArchive()

        # Add global container stack data to the archive.
        global_container_stack = Application.getInstance().getGlobalContainerStack()
        global_stack_file = zipfile.ZipInfo("Cura/%s.stack.cfg" % global_container_stack.getId())
        global_stack_file.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(global_stack_file, global_container_stack.serialize())

        # Close the archive & reset states.
        archive.close()
        mesh_writer.setStoreArchive(False)
        return True
