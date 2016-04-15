# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import copy

from UM.Logger import Logger

from UM.Math.Vector import Vector

from UM.View.GL.OpenGL import OpenGL

vertexBufferProperty = "__gl_vertex_buffer"
indexBufferProperty = "__gl_index_buffer"


##  The RenderBatch class represent a batch of objects that should be rendered.
#
#   Each RenderBatch contains a list of objects to render and all state related
#   to those objects. It tries to minimize changes to state between render the
#   individual objects. This means that for example the ShaderProgram used is
#   only bound once, at the start of rendering. There are a few values, like
#   the model-view-projection matrix that are updated for each object.
class RenderBatch():
    ##  The type of render batch.
    #
    #   This determines some basic state values, like blending on/off and additionally
    #   is used to determine sorting order.
    class RenderType:
        NoType = 0 ## No special state changes are done.
        Solid = 1 ## Depth testing and depth writing are enabled.
        Transparent = 2 ## Depth testing is enabled, depth writing is disabled.
        Overlay = 3 ## Depth testing is disabled.

    ##  The mode to render objects in. These correspond to OpenGL render modes.
    class RenderMode:
        Points = 0x0000
        Lines = 0x0001
        LineLoop = 0x0002
        LineStrip = 0x0003
        Triangles = 0x0004
        TriangleStrip = 0x0005
        TriangleFan = 0x0006

    ##  Blending mode.
    class BlendMode:
        NoBlending = 0 ## Blending disabled.
        Normal = 1 ## Standard alpha blending, mixing source and destination values based on respective alpha channels.
        Additive = 2 ## Additive blending, the value of the rendered pixel is added to the color already in the buffer.

    ##  Init method.
    #
    #   \param shader The shader to use for this batch.
    #   \param kwargs Keyword arguments.
    #                 Possible values:
    #                 - type: The RenderType to use for this batch. Defaults to RenderType.Solid.
    #                 - mode: The RenderMode to use for this batch. Defaults to RenderMode.Triangles.
    #                 - backface_cull: Whether to enable or disable backface culling. Defaults to True.
    #                 - range: A tuple indicating the start and end of a range of triangles to render. Defaults to None.
    #                 - sort: A modifier to influence object sorting. Lower values will cause the object to be rendered before others. Mostly relevant to Transparent mode.
    #                 - blend_mode: The BlendMode to use to render this batch. Defaults to NoBlending when type is Solid, Normal when type is Transparent or Overlay.
    #                 - state_setup_callback: A callback function to be called just after the state has been set up but before rendering.
    #                                         This can be used to do additional alterations to the state that can not be done otherwise.
    #                                         The callback is passed the OpenGL bindings object as first and only parameter.
    #                 - state_teardown_callback: A callback similar to state_setup_callback, but called after everything was rendered, to handle cleaning up state changes made in state_setup_callback.
    def __init__(self, shader, **kwargs):
        self._shader = shader
        self._render_type = kwargs.get("type", self.RenderType.Solid)
        self._render_mode = kwargs.get("mode", self.RenderMode.Triangles)
        self._backface_cull = kwargs.get("backface_cull", False)
        self._render_range = kwargs.get("range", None)
        self._sort_weight = kwargs.get("sort", 0)
        self._blend_mode = kwargs.get("blend_mode", None)
        if not self._blend_mode:
            self._blend_mode = self.BlendMode.NoBlending if self._render_type == self.RenderType.Solid else self.BlendMode.Normal
        self._state_setup_callback = kwargs.get("state_setup_callback", None)
        self._state_teardown_callback = kwargs.get("state_teardown_callback", None)
        self._items = []

        self._view_matrix = None
        self._projection_matrix = None
        self._view_projection_matrix = None

        self._gl = OpenGL.getInstance().getBindingsObject()

    ##  The RenderType for this batch.
    @property
    def renderType(self):
        return self._render_type

    ##  The RenderMode for this batch.
    @property
    def renderMode(self):
        return self._render_mode

    ##  The shader for this batch.
    @property
    def shader(self):
        return self._shader

    ##  Whether backface culling is enabled or not.
    @property
    def backfaceCull(self):
        return self._backface_cull

    ##  The range of elements to render.
    #
    #   \return The range of elements to render, as a tuple of (start, end)
    @property
    def renderRange(self):
        return self._render_range

    ##  The items to render.
    #
    #   \return A list of tuples, where each item is (transform_matrix, mesh, extra_uniforms)
    @property
    def items(self):
        return self._items

    ##  Less-than comparison method.
    #
    #   This sorts RenderType.Solid before RenderType.Transparent
    #   and RenderType.Transparent before RenderType.Overlay.
    def __lt__(self, other):
        if self._render_type == other._render_type:
            return self._sort_weight < other._sort_weight

        if self._render_type == self.RenderType.Solid:
            return True

        if self._render_type == self.RenderType.Transparent and other._render_type != self.RenderType.Solid:
            return True

        return False

    ##  Add an item to render to this batch.
    #
    #   \param transformation The transformation matrix to use for rendering the item.
    #   \param mesh The mesh to render with the transform matrix.
    #   \param uniforms A dict of additional uniform bindings to set when rendering the item.
    #                   Note these are set specifically for this item.
    def addItem(self, transformation, mesh, uniforms = None):
        if not transformation:
            Logger.log("w", "Tried to add an item to batch without transformation")
            return
        if not mesh:
            Logger.log("w", "Tried to add an item to batch without mesh")
            return

        self._items.append({ "transformation": transformation, "mesh": mesh, "uniforms": uniforms})

    ##  Render the batch.
    #
    #   \param camera The camera to render from.
    def render(self, camera):
        self._shader.bind()

        if self._backface_cull:
            self._gl.glEnable(self._gl.GL_CULL_FACE)
        else:
            self._gl.glDisable(self._gl.GL_CULL_FACE)

        if self._render_type == self.RenderType.Solid:
            self._gl.glEnable(self._gl.GL_DEPTH_TEST)
            self._gl.glDepthMask(self._gl.GL_TRUE)
        elif self._render_type == self.RenderType.Transparent:
            self._gl.glEnable(self._gl.GL_DEPTH_TEST)
            self._gl.glDepthMask(self._gl.GL_FALSE)
        elif self._render_type == self.RenderType.Overlay:
            self._gl.glDisable(self._gl.GL_DEPTH_TEST)

        if self._blend_mode == self.BlendMode.NoBlending:
            self._gl.glDisable(self._gl.GL_BLEND)
        elif self._blend_mode == self.BlendMode.Normal:
            self._gl.glEnable(self._gl.GL_BLEND)
            self._gl.glBlendFunc(self._gl.GL_SRC_ALPHA, self._gl.GL_ONE_MINUS_SRC_ALPHA)
        elif self._blend_mode == self.BlendMode.Additive:
            self._gl.glEnable(self._gl.GL_BLEND)
            self._gl.glBlendFunc(self._gl.GL_SRC_ALPHA, self._gl.GL_ONE)

        if self._state_setup_callback:
            self._state_setup_callback(self._gl)

        self._view_matrix = camera.getWorldTransformation().getInverse()
        self._projection_matrix = camera.getProjectionMatrix()
        self._view_projection_matrix = camera.getProjectionMatrix().multiply(self._view_matrix)

        self._shader.updateBindings(
            view_matrix = self._view_matrix,
            projection_matrix = self._projection_matrix,
            view_projection_matrix = self._view_projection_matrix,
            view_position = camera.getWorldPosition(),
            light_0_position = camera.getWorldPosition() + Vector(0, 50, 0)
        )

        for item in self._items:
            self._renderItem(item)

        if self._state_teardown_callback:
            self._state_teardown_callback(self._gl)

        self._shader.release()

    def _renderItem(self, item):
        transformation = item["transformation"]
        mesh = item["mesh"]

        normal_matrix = None
        if mesh.hasNormals():
            normal_matrix = copy.deepcopy(transformation)
            normal_matrix.setRow(3, [0, 0, 0, 1])
            normal_matrix.setColumn(3, [0, 0, 0, 1])
            normal_matrix = normal_matrix.getInverse().getTransposed()

        model_view_matrix = copy.deepcopy(transformation).preMultiply(self._view_matrix)
        model_view_projection_matrix = copy.deepcopy(transformation).preMultiply(self._view_projection_matrix)

        self._shader.updateBindings(
            model_matrix = transformation,
            normal_matrix = normal_matrix,
            model_view_matrix = model_view_matrix,
            model_view_projection_matrix = model_view_projection_matrix
        )

        if item["uniforms"] is not None:
            self._shader.updateBindings(**item["uniforms"])

        vertex_buffer = OpenGL.getInstance().createVertexBuffer(mesh)
        vertex_buffer.bind()

        index_buffer = OpenGL.getInstance().createIndexBuffer(mesh)
        if index_buffer is not None:
            index_buffer.bind()

        self._shader.enableAttribute("a_vertex", "vector3f", 0)
        offset = mesh.getVertexCount() * 3 * 4

        if mesh.hasNormals():
            self._shader.enableAttribute("a_normal", "vector3f", offset)
            offset += mesh.getVertexCount() * 3 * 4

        if mesh.hasColors():
            self._shader.enableAttribute("a_color", "vector4f", offset)
            offset += mesh.getVertexCount() * 4 * 4

        if mesh.hasUVCoordinates():
            self._shader.enableAttribute("a_uvs", "vector2f", offset)
            offset += mesh.getVertexCount() * 2 * 4

        if mesh.hasIndices():
            if self._render_range is None:
                if self._render_mode == self.RenderMode.Triangles:
                    self._gl.glDrawElements(self._render_mode, mesh.getFaceCount() * 3 , self._gl.GL_UNSIGNED_INT, None)
                else:
                    self._gl.glDrawElements(self._render_mode, mesh.getFaceCount(), self._gl.GL_UNSIGNED_INT, None)
            else:
                if self._render_mode == self.RenderMode.Triangles:
                    self._gl.glDrawRangeElements(self._render_mode, self._render_range[0], self._render_range[1], self._render_range[1] - self._render_range[0], self._gl.GL_UNSIGNED_INT, None)
                else:
                    self._gl.glDrawRangeElements(self._render_mode, self._render_range[0], self._render_range[1], self._render_range[1] - self._render_range[0], self._gl.GL_UNSIGNED_INT, None)
        else:
            self._gl.glDrawArrays(self._render_mode, 0, mesh.getVertexCount())

        self._shader.disableAttribute("a_vertex")
        self._shader.disableAttribute("a_normal")
        self._shader.disableAttribute("a_color")
        self._shader.disableAttribute("a_uvs")
        vertex_buffer.release()

        if index_buffer is not None:
            index_buffer.release()
