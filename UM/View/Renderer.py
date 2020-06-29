# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional, Dict

from UM.SortedList import SortedListWithKey
from UM.View.RenderPass import RenderPass #For typing.
from UM.Scene.SceneNode import SceneNode #For typing.


class Renderer:
    """Abstract base class for different rendering implementations.

    The renderer is used to perform rendering of objects. It abstracts away any
    details about the underlying graphics API that is used to render. It is designed
    to perform different stages of rendering, with the application indicating which
    objects should be rendered but the actual rendering process happening after a
    sorting step.
    """
    def __init__(self) -> None:
        super().__init__()

        self._render_passes = SortedListWithKey(key = lambda k: k.getPriority()) #type: SortedListWithKey

        self._render_passes_by_key = {} # type: Dict[str, RenderPass]

    def beginRendering(self) -> None:
        """Signal the beginning of the rendering process.

        This should set up any required state before any actual rendering happens.
        """
        raise NotImplementedError()

    def queueNode(self, node: SceneNode, **kwargs) -> None:
        """Queue a node to be rendered.

        :param node: The node to queue for rendering.
        :param kwargs: Keyword arguments.
        Most of these are passed to the RenderBatch constructor directly. See RenderBatch for all available options.
        In addition, the parameter "shader" is available, which determines the shader to render with. When not specified,
        it defaults to a simple vertex color shader.
        """
        raise NotImplementedError()

    def render(self) -> None:
        """Render everything that was set up to be rendered."""
        raise NotImplementedError()

    def endRendering(self) -> None:
        """Finish rendering, finalize and clear state."""
        raise NotImplementedError()

    def addRenderPass(self, render_pass: RenderPass) -> None:
        """Add a render pass that should be rendered.

        :param render_pass: The render pass to add.
        """
        self._render_passes.add(render_pass)
        self._render_passes_by_key[render_pass.getName()] = render_pass

    def removeRenderPass(self, render_pass: RenderPass) -> None:
        """Remove a render pass from the list of render passes to render.

        :param render_pass: The render pass to remove.
        """
        if render_pass in self._render_passes:
            self._render_passes.remove(render_pass)
        del self._render_passes_by_key[render_pass.getName()]

    def getRenderPass(self, name: str) -> Optional[RenderPass]:
        """Get a render pass by name.

        :param name: The name of the render pass to get.

        :return: The named render pass or None if not found.
        """

        return self._render_passes_by_key.get(name)

    def getRenderPasses(self) -> SortedListWithKey:
        """Get the list of all render passes that should be rendered."""
        return self._render_passes
