from LocalFileStorageDevice import LocalFileStorageDevice

import platform

def getMetaData():
    return { "name": "Local File Storage", "type": "StorageDevice" }

def register(app):
    device = LocalFileStorageDevice()
    app.addStorageDevice("local", device)
    
    if platform.system() == "Windows":
        from WindowsRemovableStorageThread import WindowsRemoveableStorageThread
        thread = WindowsRemovableStorageThread(app)
        thread.start()
    elif platform.system() == "Darwin":
        from OSXRemovableStorageThread import OSXRemovableStorageThread
        thread = OSXRemovableStorageThread(app)
        thread.start()
    elif platform.system() == "Linux":
        from LinuxRemovableStorageThread import LinuxRemovableStorageThread
        thread = LinuxRemovableStorageThread(app)
        thread.start()
    else:
        print("Unsupported system " + platform.system() + ", no removable device hotplugging support available.")
