Plugins in Uranium
==================

The PluginRegistry class is responsible for loading plugins and their
metadata. Plugins are expected to be Python modules with an `__init__.py`
file that provides a `getMetaData()` and a `register()` function. Plugins
are loaded from all configured plugin paths. The `register()` function is
expected to return a dictionary of plugin type -> object pairs that should be
registered. Registration happens by the PluginRegistry based on plugin type.

Plugin Metadata
---------------
The `getMetaData()` function should return a dictionary object containing metadata
for the plugin. The contents of this dictionary are dependent on the plugin types
the plugin wishes to register. Each key in the dictionary should correspond to a
plugin type, with the exception of the plugin about data (see below).

### Plugin About Data

Each plugin must provide meta data about the actual plugin. This should be
provided by a dictionary assigned to the key 'plugin' in the plugin's meta data.
At the very least, this dictionary must contain a key "api". The "api" key should
contain an integer value representing the Uranium API the plugin was designed for.
This key is used to identify compatible plugins. If the api value does not match
the current API version as defined in PluginRegistry, the plugin will not be loaded.
This is done to prevent outdated plugins from taking down the entire application
due to API changes.

In addition to the API version, the plugin about data can contain some information
about the actual plugin. These are "name", "author", "version" and "description".
The name field should provide a human-readable name for the plugin. The author field
should provide information about who created the plugin. The description should
provide a short description about what the plugin does. Finally, the version field
should provide a user-visible version string so new versions can be distinguished.

Plugin Types
------------

Plugin types are registered using the `addType()` method of PluginRegistry. Please
see that method for more information on how to add plugin types. Uranium defines a
set of plugin types that are expected to be useful to all applications using Uranium.
However, should you wish to extend this, the possibilities are there. The following
plugin types are registered by objects in the Uranium framework:

Note: While it is currently possible to define multiple plugin types in a plugin, it
is not possible to define the same plugin type twice, since there is no way to
distinguish one set of metadata from another.

- mesh_reader
- mesh_writer
- logger
- input_device
- output_device
- tool
- view
- extension
- backend

=== Mesh Reader

Mesh reader plugins provide functionality to read certain file formats. They are used
when a user tries to open a file through an open file dialog or similar method. Mesh
reader plugins require metadata in the plugin metadata, in the form of a list of
dictionaries. The list should use the key "mesh_reader", with each entry describing
an input file format. Each entry in the list should contain an "extension" and
"description" entry. The extension defines what extension the plugin supports, the
description provides a human-readable description of the file format. Note that this
description should be short enough to fit in the file type combo box of an open file
dialog.

=== Mesh Writer

Mesh writer plugins provide functionality to write certain file formats. They are used
when an application needs to write mesh files. One example is when saving through a file
save dialog, but they are primarily intended to be used with OutputDevice classes. Mesh
writer plugins require metadata in the plugin metadata. Currently, a single key "output"
is used. That should contain a list of dictionaries, where each dictionary describes a
single output format. Each dictionary is expected to contain four entries: extension,
description, mime_type and mode. Extension is the extension usually used for this output
format and will often automatically be appended to the file name. Description is a human-
readable description of the file format, that should be short enough to fit in a file
save dialog. The mime_type entry contains the mime type for this format. This is the
primary means used to look up mesh writers. Finally, the mode value should be either
one of the values from MeshWriter.OutputMode. Currently, these are either TextMode or
BinaryMode. This entry determines in what way the output stream passed to the plugin
is opened.

=== Logger

Logger plugins provide logging output functionality, such as writing log information to
a file. These require no special metadata.

=== Output Device

Output device plugins provide a factory object that creates a certain type of output
device. They require no special metadata.

=== Tool

=== View

=== Extension

=== Backend


Example Plugin Metadata
-----------------------

'''
{
    "plugin":
    {
        "name": "Example Plugin",
        "description": "A plugin example",
        "author": "Example Author",
        "version": "0.0",
        "api": 2
    },
    "mesh_reader":
    [
        {
            "extension": "example",
            "description": "Example File"
        }
    ],
    "mesh_writer":
    [
        {
            "extension": "example",
            "description": "Example File",
            "mime_type": "application/x-example",
            "mode": MeshWriter.OutputMode.TextMode
        }
    ]
}
'''
