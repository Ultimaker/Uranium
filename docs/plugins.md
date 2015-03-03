Writing Plugins
===============

The PluginRegistry class is responsible for loading plugins and their
metadata. Plugins are expected to be Python modules with an `__init__.py`
file that provides a `getMetaData()` and a `register()` function. Plugins
are loaded from all configured plugin paths. The `register()` function is
expected to return one or a list of objects that should be registered.
Registration happens by the PluginRegistry based on plugin type. The
`getMetaData()` function should return a dictionary object containing metadata
for the plugin.


Plugin Types
------------

- MeshHandler
- Logger
- StorageDevice
- Tool
- View
- Extension
- Backend
