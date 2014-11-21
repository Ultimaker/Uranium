
## Encapsulates a number of different ways of storing file data.
#
class StorageDevice(object):
    def __init__(self):
        super(StorageDevice, self).__init__() # Call super to make multiple inheritence work.
        self._properties = {}
    
    ## Open a file so it can be read from or written to.
    #  \param file_name The name of the file to open. Can be ignored if not applicable.
    #  \param mode What mode to open the file with. See Python's open() function for details. Can be ignored if not applicable.
    #  \return An open stream that can be read from or written to.
    def openFile(self, file_name, mode):
        raise NotImplementedError()
