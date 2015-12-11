Rendering
=========

Uranium uses a model-view-controller like approach for the scene and its
contents. In this approach, the model is represented by the Scene class and the
SceneNode classes contained in the Scene. The controller part is handled by the
Controller class and by Tool subclasses. Finally, the View class handles
everything related to viewing the current scene. This means that the current
active View is always in control of what and how things are rendered. While
certain things can default to certain behaviour, the View is always capable of
overwriting this behaviour.

Of course, the View does not need to handle everything on its own. Since
rendering is done through OpenGL, there are several convenience classes that are
meant to simplify handling of OpenGL and possible different bindings to OpenGL.
In addition, the Renderer, RenderBatch and RenderPass classes are important
classes that separate common functionality.

Rendering Pipeline
------------------

Rendering starts somewhere in the toolkit's event handling, when the toolkit
determines that everything should be repainted. This will usually send a paint
event to the main window. The main window then processes this event and starts
the rendering process. At this point, two objects are required. One is an
instance of Renderer, which is a single, unique instance for the application.
The other is an instance of the current active View. First,
Renderer::beginRendering() is called to make sure OpenGL is set up for
rendering.

After that, View::beginRendering() is called so the View can determine what
should be rendered. In the View's beginRendering() implementation, the View
should make calls to Renderer::queueNode() to queue nodes that should be
rendered. Additionally, the View can create additional RenderPass instances that
should be used for rendering the current View. Once the view is done with
queueing nodes, Renderer::render() is called. This will perform sorting of items
that need to be rendered and any other post processing that needs to happen on
the list of things to render, then go through the list of RenderPass instances
and call RenderPass::render() on each. RenderPass::render() performs the actual
rendering of the objects, so that once the last RenderPass is rendered, a
rendered image should be ready to put on the screen.

Finally, when Renderer::render() is done, first View::endRendering() is called
to make sure the View can do any clean up it needs, and after that
Renderer::endRendering() is called to also give the Renderer a chance to clean
up.

Render Passes
-------------

While the View is the final arbiter on what and how things are rendered,
RenderPass objects also have a large say in the matter. Each RenderPass
describes a single pass of rendering the objects in the scene. These passes can
vary greatly in how they render things and can even vary what they render.

By default, there are three RenderPass instances defined by Uranium. The first
RenderPass is the selection pass. This will render all selectable objects to a
texture that can then be queried to get what object is currently under the
cursor. The next pass is the DefaultPass. This pass simply renders everything
that was specified by the View to a texture. The last pass is the CompositePass.
This pass is enforced to be the last RenderPass, as it combines the previous
passes into a final image to be rendered to screen. By default, it will render
the contents of the DefaultPass to a full-screen quad, then use the
SelectionPass to render an outline around selected objects. The CompositePass's
shader and bindings can be freely changed when needed, though this should mostly
be left up to the View.

SceneNode::render() versus Renderer::queueNode()
------------------------------------------------

One thing to note when implementing View subclasses is that certain SceneNode
subclasses want to be able to determine their own way of rendering. This is done
through reimplementing the SceneNode::render() method. Views should make sure to
call this when they want the default rendering behaviour, or when rendering
certain SceneNode subclasses. For example, the Platform class makes sure to
always queue the Platform mesh with the right shaders for rendering the
platform. If SceneNode::render() returns False, this means that the SceneNode
does not need to control its own rendering and can be rendered any way the View
wants. The View should then proceed to use queueNode() to render the node. Note
that the View is still in complete control, since it can simply ignore objects
that want to do custom rendering and render them any way it likes.
