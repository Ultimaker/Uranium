
## Encapsulates a number of different ways of storing file data.
#
class StorageDevice(object):
    def __init__(self):
        super(StorageDevice, self).__init__() # Call super to make multiple inheritence work.
    
    ## Open a file so it can be read from or written to.
    #  \param file_name \type{string} The name of the file to open. Can be ignored by subclasses if not applicable.
    #  \param mode \type{string} What mode to open the file with. See Python's `open()` function for details. Can be ignored by subclasses if not applicable.
    #  \return \type{io.IOBase} An open stream that can be read from or written to.
    def openFile(self, file_name, mode):
        raise NotImplementedError("openFile should be reimplemented by subclasses")

    ##  Close a file cleanly.
    #   \param file \type{io.IOBase} The file to close. This should be an object as returned by openFile.
    def closeFile(self, file):
        raise NotImplementedError("closeFile should be reimplemented by subclasses")
