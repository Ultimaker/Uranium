from UM.MeshHandling.MeshWriter import MeshWriter
import time
##      Class to write the PCD format to file. See http://pointclouds.org/documentation/tutorials/pcd_file_format.php 
#       for more information on the format.        
class PCDWriter(MeshWriter):
    def __init__(self):
        super(PCDWriter, self).__init__()
        self._supported_extension = ".pcd"
        
    ##  Write the Mesh (pointcloud!) to file.
    #   \param file_name Location to write to
    #   \param storage_device Device to write to.
    #   \param mesh_data MeshData to write.
    #   \returns True if it was able to write, False otherwise (either due to error, or unable to do something with extension).
    def write(self, file_name, storage_device, mesh_data):
        if(self._supported_extension in file_name):
            num_verts = mesh_data.getNumVerts()
            vertices = mesh_data.getVertices()
            f = storage_device.openFile(file_name, 'wb')
            f.write(("#PLUGGABLE UNICORN ASCII PCD EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S')).ljust(80, '\000'))
            f.write("VERSION .7") # We're using PCL version .7
            f.write("FIELDS x y z normal_x normal_y normal_z ") # Points are saved with a normal
            f.write("SIZE 4 4 4 4 4 4") # Data is saved as floats (4 bytes each)
            f.write("TYPE f f f f f f") # Data is float
            f.write("COUNT 1 1 1 1 1 1") # Each data element is of size 1
            f.write("WIDTH %s" % num_verts) # We save it as an unordend pointcloud
            f.write("HEIGHT 1") # Unordend, so height is 1
            f.write("VIEWPOINT 0 0 0 1 0 0 0") # Translation + quaternion
            f.write("POINTS %s" % num_verts) # Number of points in cloud
            f.write("DATA ascii") # Save data as ascii
            for vertex in vertices:
                position = vertex.getPosition()
                normal = vertex.getNormal()
                f.write("%s %s %s", position.x(),position.y(),position.z(),normal.x(),normal.y(),normal.z())
                
            storage_device.closeFile(f)
            return True
        else:
            return False
