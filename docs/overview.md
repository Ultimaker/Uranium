High Level Overview
===================

The Uranium framework consists of several parts, divided over several
modules. These modules are Core, Backend, Math, Mesh, Scene, Settings
and View. In addition, there are two toolkit-specific modules that
implement a lot of UI bits for the applications.

Core
----

The %Core module is formed of base classes and central objects relevant
to all applications. Primary among these are the [PluginRegistry] and
[Application] classes. The Application class is the central object of any
application. Its primary function is providing a central access point
for other central objects like the Controller and MeshFileHandler.

The PluginRegistry class is responsible for loading plugins and their
metadata. For more details on writing plugins, see [plugins].

Another important class is the [Signal] class. This provides a mechanism for
simplified event handling using callbacks. This is used throughout the
library for handling events. For example, the Controller class provides
an activeViewChanged signal that gets emitted whenever the active view
changes. Other classes can connect to this signal to receive notifications
about this event.

Other classes part of the core are the [Controller], which is a central object
providing communication between the Scene and the View classes, in
addition to handling events between scene, view, input device and tools. The
[Event] class represents the base class for any event in the system, with
several subclasses provided for common events. [InputDevice] is an abstract
base class for devices providing input to tools and/or view and should be
subclassed by plugins that want to provide custom input devices. [Logger] is
a base class for classes that log to a certain output. These can be
subclassed by plugins to provide alternative logging capabilities.
[StorageDevice] provides an abstraction around file opening and closing, it
should be subclassed by plugins that want to do things like provide file
uploading. Finally, [Tool] is the base class for any tool that operates on
the scene.

[PluginRegistry]: \ref Cura#PluginRegistry#PluginRegistry
[Application]:    \ref Cura#Application#Application
[Signal]:         \ref Cura#Signal#Signal
[Controller]:     \ref Cura#Controller#Controller
[Event]:          \ref Cura#Event#Event
[InputDevice]:    \ref Cura#InputDevice#InputDevice
[Logger]:         \ref Cura#Logger#Logger
[StorageDevice]:  \ref Cura#StorageDevice#StorageDevice
[Tool]:           \ref Cura#Tool#Tool
[plugins]:        plugins.md

Backend
-------

The %Backend module provides classes relating to the communication with
external applications with the intent of processing data. The prime example
of this functionality is the communication with the CuraEngine slicing
engine.

The primary class to facilitate this functionality is the [Backend] class.
It provides an abstract base that should be subclassed by plugins that want
to provide backend functionality. The backend class provides a list of the
commands that are supported by that backend. The [Command] class encapsulates
these commands and provides the actual implementation of the command in its
`send()` and `receive()` methods. The commands talk to the actual backend
application over a local TCP socket as provided by the [Socket] class. This
class creates a system socket that is used for the communication with the
backend. The Command objects are responsible for serialising and deserialising
the actual data sent over this socket.

[Backend]: \ref Cura#Backend#Backend#Backend
[Command]: \ref Cura#Backend#Command#Command
[Socket]:  \ref Cura#Backend#Socket#Socket

Math
----

The %Math module provides classes for dealing with linear algebra. It
includes a [Matrix], [Vector] and [Quaternion] class that are based on Numpy
arrays and implement basic 4x4 affine transformation logic. These are
primarily used by SceneNode and related objects for their transformations.

[Matrix]:     \ref Cura#Math#Matrix#Matrix
[Vector]:     \ref Cura#Math#Vector#Vector
[Quaternion]: \ref Cura#Math#Quaternion#Quaternion

MeshHandling
------------

The %MeshHandling module provides several classes for dealing with mesh data.
The primary class for this module is [MeshFileHandler], which gets created by
the Application object and provides read and write capabilities for meshes. It
uses a list of [MeshReader] and [MeshWriter] objects that implement the actual
mesh reading and writing logic. These two classes should be subclassed by plugins
that want to provide suport for reading and or writing a certain mesh format.

When reading a mesh, the MeshFileHandler returns a [MeshData] object which is the
internal data object for storing mesh data. MeshData consists primarily of a list
of [Vertex] objects with a list of indices that form the faces of the mesh. It
also provides convenience methods for dealing with this mesh data.

[MeshFileHandler]: \ref Cura#MeshHandling#MeshFileHandler#MeshFileHandler
[MeshReader]:      \ref Cura#MeshHandling#MeshReader#MeshReader
[MeshWriter]:      \ref Cura#MeshHandling#MeshWriter#MeshWriter
[MeshData]:        \ref Cura#MeshHandling#MeshData#MeshData
[Vertex]:          \ref Cura#MeshHandling#Vertex#Vertex

Scene
-----

The %Scene module provides classes that handle all the data in the scene. The
scene itself is represented by the [Scene] class. The Scene class provides the
root [SceneNode] object. The SceneNode is a node in a tree of nodes that form
the scene graph. Each scene node has a transformation and can provide that
transformation relative to its parents. In addition to the root scene node, the
Scene class also provides the active [Camera] object.

[Scene]:     \ref Cura#Scene#Scene#Scene
[SceneNode]: \ref Cura#Scene#SceneNode#SceneNode
[Camera]:    \ref Cura#Scene#Camera#Camera

Settings
--------

The %Settings module provides classes for handling machine settings. The [MachineSettings]
class provides a central object to read and write all settings related to a machine.
It provides a list of [SettingsCategory] objects. Each settings category then provides
a tree of [Setting] objects that are used to represent the settings of the machine.
The leaves of this tree represent more detailed settings, for example, a "Speed" setting
could have a "Wall Speed" and an "Infill Speed" setting as children. The MachineSettings
class can load this tree structure from a JSON file and also store the values in an ini
file.

The Validators submodule of the settings module provides several classes that are used
to validate settings. These validators are created by the MachineSettings object as
specified in the JSON it loads. They are supplied with an error range, a warning range
and a safe range.

[MachineSettings]:  \ref Cura#Settings#MachineSettings#MachineSettings
[SettingsCategory]: \ref Cura#Settings#SettingsCategory#SettingsCategory
[Setting]:          \ref Cura#Settings#Setting#Setting

View
----

The %View module contains base classes for views and renderers. Plugins that want
to provide a view should subclass the [View] class. The view class controls the
complete rendering path and should decide how everything is rendered. It should
make use of the renderer provided by the application to render the scene. The
[Renderer] is created by the application and abstracts the underlying graphics API.

[View]:     \ref Cura#View#View#View
[Renderer]: \ref Cura#View#Renderer#Renderer

Toolkit Specifics
-----------------

Most of the library does not contain any toolkit specific code. Instead, most toolkit
specific code is contained in a toolkit-specific submodule. Currently, this concerns the
Qt submodule, which contains toolkit specific classes that implement most of the UI bits
on top of Qt, using PyQt.

Class Diagram
-------------
![Pluggable Unicorn Class Diagram](classes.png)
