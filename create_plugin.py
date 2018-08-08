import argparse
import os.path
import zipfile

def checkValidPlugin(path):
    # A plugin must be a folder
    if not os.path.isdir(path):
        return False

    # A plugin must contain an __init__.py
    if not os.path.isfile(os.path.join(path, "__init__.py")):
        return False
    
    # .. and a plugin must contain an plugin.json!
    if not os.path.isfile(os.path.join(path, "plugin.json")):
        return False

    return True

def zipDirectory(path, zip_handle):
    # zip_handle is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            filename = os.path.join(root, file)
            if os.path.isfile(filename) and not file.startswith(".git") and ".git" not in root:
                _, extension = os.path.splitext(filename)
                if extension not in excluded_extentions:
                    zip_handle.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

excluded_extentions = [".pyc", ".umplugin"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin_location", type = str, help = "Location of plugin folder")
    args = parser.parse_args()

    full_plugin_path = os.path.join(os.getcwd(), args.plugin_location)

    if not checkValidPlugin(full_plugin_path):
        print("Provided plug-in location is not a valid plug-in folder.")
        exit()

    plugin_name = os.path.basename(os.path.normpath(full_plugin_path))
    plugin_file_location = plugin_name + ".umplugin"
    with zipfile.ZipFile(plugin_file_location, "w") as plugin_zip:
        # Ensure that the root folder is created correctly. We need to tell zip to not compress the folder!
        subdirectory = zipfile.ZipInfo(plugin_name + "/")
        plugin_zip.writestr(subdirectory, "", compress_type = zipfile.ZIP_STORED) #Writing an empty string creates the directory.
        zipDirectory(full_plugin_path, plugin_zip)
    print("Done!")