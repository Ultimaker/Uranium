# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import copy

from PyQt5.QtGui import QOpenGLBuffer

from UM.Math.Vector import Vector

from UM.View.GL.OpenGL import OpenGL

vertexBufferProperty = "__gl_vertex_buffer"
indexBufferProperty = "__gl_index_buffer"

class RenderBatch():
    class RenderType:
        Solid = 1
        Transparent = 2
        Overlay = 3

    class RenderMode:
        Points = 0x0000
        Lines = 0x0001
        LineLoop = 0x0002
        LineStrip = 0x0003
        Triangles = 0x0004
        TriangleStrip = 0x0005
        TriangleFan = 0x0006

    def __init__(self, **kwargs):
        self._render_type = kwargs.get("type", self.RenderType.Solid)
        self._render_mode = kwargs.get("mode", self.RenderMode.Triangles)
        self._shader = kwargs.get("shader", None)
        self._backface_cull = kwargs.get("backface_cull", True)
        self._render_range = kwargs.get("range", None)
        self._items = []

        self._view_matrix = None
        self._projection_matrix = None

        self._gl = OpenGL.getInstance().getBindingsObject()

    @property
    def renderType(self):
        return self._render_type

    @property
    def renderMode(self):
        return self._render_mode

    @property
    def material(self):
        return self._material

    @property
    def backfaceCull(self):
        return self._backface_cull

    @property
    def renderRange(self):
        return self._render_range

    @property
    def items(self):
        return self._items

    def __lt__(self, other):
        if self._render_type == self.RenderType.Solid:
            return True

        if self._render_type == self.RenderType.Transparent and other._render_type != self.RenderType.Solid:
            return True

        return False

    def addItem(self, transform, mesh, uniforms = None):
        self._items.append((transform, mesh, uniforms))

    def render(self, camera):
        self._shader.bind()

        if self._backface_cull:
            self._gl.glEnable(self._gl.GL_CULL_FACE)
        else:
            self._gl.glDisable(self._gl.GL_CULL_FACE)

        if self._render_type == self.RenderType.Solid:
            self._gl.glDisable(self._gl.GL_BLEND)
            self._gl.glEnable(self._gl.GL_DEPTH_TEST)
            self._gl.glDepthMask(self._gl.GL_TRUE)
        if self._render_type == self.RenderType.Transparent:
            self._gl.glDepthMask(self._gl.GL_FALSE)
            self._gl.glEnable(self._gl.GL_BLEND)
            self._gl.glBlendFunc(self._gl.GL_SRC_ALPHA, self._gl.GL_ONE_MINUS_SRC_ALPHA)
        elif self._render_type == self.RenderType.Overlay:
            self._gl.glDisable(self._gl.GL_DEPTH_TEST)

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

        self._shader.release()

    def _renderItem(self, item):
        transform = item[0]
        mesh = item[1]
        if not mesh:
            return #Something went wrong, node has no mesh.

        normal_matrix = None
        if mesh.hasNormals():
            normal_matrix = copy.deepcopy(transform)
            normal_matrix.setRow(3, [0, 0, 0, 1])
            normal_matrix.setColumn(3, [0, 0, 0, 1])
            normal_matrix = normal_matrix.getInverse().getTransposed()

        model_view_matrix = copy.deepcopy(transform).preMultiply(self._view_matrix)
        model_view_projection_matrix = copy.deepcopy(transform).preMultiply(self._view_projection_matrix)

        self._shader.updateBindings(
            model_matrix = item[0],
            normal_matrix = normal_matrix,
            model_view_matrix = model_view_matrix,
            model_view_projection_matrix = model_view_projection_matrix
        )

        if item[2] is not None:
            self._shader.updateBindings(**item[2])

        vertex_buffer = None
        try:
            vertex_buffer = getattr(mesh, vertexBufferProperty)
        except AttributeError:
            pass

        if vertex_buffer is None:
            vertex_buffer =  self._createVertexBuffer(mesh)

        vertex_buffer.bind()

        if mesh.hasIndices():
            index_buffer = None
            try:
                index_buffer = getattr(mesh, indexBufferProperty)
            except AttributeError:
                pass

            if index_buffer is None:
                index_buffer = self._createIndexBuffer(mesh)

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

        if mesh.hasIndices():
            index_buffer.release()

    def _createVertexBuffer(self, mesh):
        buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        buffer.create()
        buffer.bind()

        buffer_size = mesh.getVertexCount() * 3 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasNormals():
            buffer_size += mesh.getVertexCount() * 3 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasColors():
            buffer_size += mesh.getVertexCount() * 4 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasUVCoordinates():
            buffer_size += mesh.getVertexCount() * 2 * 4 # Vertex count * number of components * sizeof(float32)

        buffer.allocate(buffer_size)

        offset = 0
        vertices = mesh.getVerticesAsByteArray()
        if vertices is not None:
            buffer.write(0, vertices, len(vertices))
            offset += len(vertices)

        if mesh.hasNormals():
            normals = mesh.getNormalsAsByteArray()
            buffer.write(offset, normals, len(normals))
            offset += len(normals)

        if mesh.hasColors():
            colors = mesh.getColorsAsByteArray()
            buffer.write(offset, colors, len(colors))
            offset += len(colors)

        if mesh.hasUVCoordinates():
            uvs = mesh.getUVCoordinatesAsByteArray()
            buffer.write(offset, uvs, len(uvs))
            offset += len(uvs)

        buffer.release()

        setattr(mesh, vertexBufferProperty, buffer)
        return buffer

    def _createIndexBuffer(self, mesh):
        buffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        buffer.create()
        buffer.bind()

        data = mesh.getIndicesAsByteArray()
        buffer.allocate(data, len(data))
        buffer.release()

        setattr(mesh, indexBufferProperty, buffer)
        return buffer
