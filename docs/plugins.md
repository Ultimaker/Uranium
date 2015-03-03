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

Application-specific overrides
------------------------------
The plugin metadata system allows overriding values based on the current
application. To use this, include a key with the application name in it, then
provide the overridden values of metadata values as elements in a dictionary.
The dictionary object that will be returned by `getMetaData()`   will have the
relevant values replaced with the application specific values.

Plugin Types
------------

Plugin types are registered using the `addType()` method of PluginRegistry.

The following plugin types are registered by objects in the Uranium framework:

- mesh_writer
- mesh_reader
- logger
- storage_device
- tool
- view
- extension
- backend
- input_device
