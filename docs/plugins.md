Writing Plugins
===============

The PluginRegistry class is responsible for loading plugins and their
metadata. Plugins are expected to be Python modules with an `__init__.py`
file that provides a `getMetaData()` and a `register()` function. Plugins
are loaded from all configured plugin paths. The `register()` function is
called to register any objects exposed by the plugin. Plugins are free to
expose any number of objects as long as they can be registered with the
rest of the system. The `getMetaData()` function should return a dictionary
object containing metadata for the plugin. For more details on writing
plugins, see [plugins].

Plugin Types
------------

- MeshHandler
- Logger
- StorageDevice
- Tool
- View
- Extension
- Backend
