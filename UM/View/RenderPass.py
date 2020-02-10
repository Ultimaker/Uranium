# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Optional, Tuple
from PyQt5.QtGui import QImage #For typing.

from UM.Logger import Logger
from UM.View.GL.OpenGL import OpenGL
from UM.View.GL.FrameBufferObject import FrameBufferObject


class RenderPass:
    """Base class for a rendering pass.

    The RenderPass class encapsulates a render pass, that is a single
    step in the rendering process.

    :note While the render pass could technically support render to
    texture without using Framebuffer Objects, the PyQt bindings object
    lacks support for any function like glReadPixels. Therefore, the
    Qt OpenGL initialization code checks for FBO support and aborts the
    program if no support is found.
    """

    MaximumPriority = 999
    """The maximum priority of a render pass. Priority should always be
    less than this.
    """

    def __init__(self, name: str, width: int, height: int, priority: int = 0) -> None:
        self._name = name #type: str
        self._width = width #type: int
        self._height = height #type: int
        self._priority = priority #type: int

        self._gl = OpenGL.getInstance().getBindingsObject()

        self._fbo = None #type: Optional[FrameBufferObject]

    def getName(self) -> str:
        """Get the name of this RenderPass.

        :return: The name of the render pass.
        """
        return self._name

    def getSize(self) -> Tuple[int, int]:
        return self._width, self._height

    def getPriority(self) -> int:
        """Get the priority of this RenderPass.

        The priority is used for ordering the render passes. Lower priority render passes
        are rendered earlier and are available for later render passes to use as texture
        sources.

        :return: The priority of this render pass.
        """
        return self._priority

    def setSize(self, width: int, height: int) -> None:
        """Set the size of this render pass.

        :param width: The new width of the render pass.
        :param height: The new height of the render pass.

        :note This will recreate the storage object used by the render
        pass. Due to that, the contents will be invalid after resizing
        until the render pass is rendered again.
        """

        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            self._fbo = None  # Ensure the fbo is re-created next render pass.

    def bind(self) -> None:
        """Bind the render pass so it can be rendered to.

        This will make sure everything is set up so the contents of
        this render pass will be updated correctly. It should be called
        as part of your render() implementation.

        :note It is very important to call release() after a call to
        bind(), once done with rendering.
        """

        if self._fbo is None:
            # Ensure that the fbo is created. This is done on (first) bind, as this needs to be done on the main thread.
            self._updateRenderStorage()

        if self._fbo:
            self._fbo.bind()

            # Ensure we can actually write to the relevant FBO components.
            self._gl.glColorMask(self._gl.GL_TRUE, self._gl.GL_TRUE,self._gl.GL_TRUE, self._gl.GL_TRUE)
            self._gl.glDepthMask(self._gl.GL_TRUE)

            self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

    def release(self) -> None:
        """Release the render pass.

        This makes sure the contents of this render pass are properly
        updated at the end of rendering.
        """

        if self._fbo is None:
            return #Already released. Nothing more to do.
        self._fbo.release()

        # Workaround for a driver bug with recent Intel chips on OSX.
        # Releasing the current FBO does not properly clear the depth buffer, so we have to do that manually.
        #if Platform.isOSX() and OpenGL.getInstance().getGPUVendor() == OpenGL.Vendor.Intel:
            #self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

    def render(self) -> None:
        """Render the contents of this render pass.

        This method should be reimplemented by subclasses to perform the
        actual rendering of the render pass.
        """

        raise NotImplementedError("Should be implemented by subclasses")

    def getTextureId(self) -> int:
        """Get the texture ID of this render pass so it can be reused by other passes.

        :return: The OpenGL texture ID used by this pass.
        """

        if self._fbo is None:
            Logger.log("w", "FrameBufferObject has been released. Can't get any frame buffer texture ID.")
            return -1
        return self._fbo.getTextureId()

    def getOutput(self) -> QImage:
        """Get the pixel data produced by this render pass.

        This returns an object that contains the pixel data for this render pass.

        :note The current object type returned is currently dependant on the specific
        implementation of the UM.View.GL.FrameBufferObject class.
        """

        if self._fbo is None:
            Logger.log("w", "FrameBufferObject has been released. Can't get frame output.")
            return QImage()
        return self._fbo.getContents()

    def _updateRenderStorage(self) -> None:
        # On Mac OS X, this function may get called by a main window resize signal during closing.
        # This will cause a crash, so don't do anything when it is shutting down.
        import UM.Qt.QtApplication
        if UM.Qt.QtApplication.QtApplication.getInstance().isShuttingDown():
            return
        if self._width <= 0 or self._height <= 0:
            Logger.log("w", "Tried to create render pass with size <= 0")
            return

        self._fbo = OpenGL.getInstance().createFrameBufferObject(self._width, self._height)
