from PyQt5.QtGui import QColor, QOpenGLBuffer, QOpenGLContext, QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat, QSurfaceFormat, QOpenGLVersionProfile, QImage

from UM.Application import Application
from UM.View.Renderer import Renderer
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Resources import Resources
from UM.Logger import Logger
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.Selection import Selection
from UM.Scene.PointCloudNode import PointCloudNode
from UM.Math.Color import Color

from . import QtGL2Material

import numpy
from ctypes import c_void_p

vertexBufferProperty = '__qtgl2_vertex_buffer'
indexBufferProperty = '__qtgl2_index_buffer'

##  A Renderer implementation using OpenGL2 to render.
class QtGL2Renderer(Renderer):
    def __init__(self):
        super().__init__()

        self._controller = Application.getInstance().getController()
        self._scene = self._controller.getScene()

        self._vertexBufferCache = {}
        self._indexBufferCache = {}

        self._initialized = False

        self._lightPosition = Vector(0, 0, 0)
        self._backgroundColor = QColor(128, 128, 128)
        self._viewportWidth = 0
        self._viewportHeight = 0

        self._solidsQueue = []
        self._transparentQueue = []
        self._overlayQueue = []

        self._render_selection = True
        self._selection_buffer = None
        self._selection_map = {}
        self._selection_image = None

        self._camera = None

    def createMaterial(self, vert, frag):
        mat = QtGL2Material.QtGL2Material(self)
        mat.loadVertexShader(vert)
        mat.loadFragmentShader(frag)
        mat.build()
        return mat

    def createFrameBuffer(self, width, height):
        buffer_format = QOpenGLFramebufferObjectFormat()
        buffer_format.setAttachment(QOpenGLFramebufferObject.Depth)
        return QOpenGLFramebufferObject(width, height, buffer_format)

    def setLightPosition(self, position):
        self._lightPosition = position

    def setBackgroundColor(self, color):
        self._backgroundColor = color

    def setViewportSize(self, width, height):
        self._viewportWidth = width
        self._viewportHeight = height

    def getSelectionColorAtCoordinate(self,x,y):
        if not self._selection_image:
            return None
        px = (0.5 + x / 2.0) * self._viewportWidth
        py = (0.5 + y / 2.0) * self._viewportHeight
        return Color.fromARGB(self._selection_image.pixel(px,py))

    def getIdAtCoordinate(self, x, y, sample_radius = 1):
        if not self._selection_image:
            return None

        px = (0.5 + x / 2.0) * self._viewportWidth
        py = (0.5 + y / 2.0) * self._viewportHeight

        samples = []
        if sample_radius == 1:
            if px < 0 or px > (self._selection_image.width() - 1) or py < 0 or py > (self._selection_image.height() - 1):
                return None

            pixel = self._selection_image.pixel(px, py)
            samples.append(Color.fromARGB(pixel))
        else:
            for sx in range(-sample_radius, sample_radius):
                if px + sx < 0 or px + sx > (self._selection_image.width() - 1):
                    continue
                for sy in range(-sample_radius, sample_radius):
                    if py + sy < 0 or py + sy > (self._selection_image.height() - 1):
                        continue

                    pixel = self._selection_image.pixel(px + sx, py + sy)
                    samples.append(Color.fromARGB(pixel))

        idCount = {}
        for sample in samples:
            if sample in self._selection_map:
                if not self._selection_map[sample] in idCount:
                    idCount[self._selection_map[sample]] = 1
                else:
                    idCount[self._selection_map[sample]] += 1
        if len(idCount) > 0:
            return max(idCount)
        else:
            return None

    def setRenderSelection(self, render):
        self._render_selection = render

    def beginRendering(self):
        if not self._initialized:
            self._initialize()

        self._gl.glViewport(0, 0, self._viewportWidth, self._viewportHeight)
        self._gl.glClearColor(self._backgroundColor.redF(), self._backgroundColor.greenF(), self._backgroundColor.blueF(), self._backgroundColor.alphaF())
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

        if not QOpenGLContext.currentContext().format().renderableType() == QSurfaceFormat.OpenGLES:
            self._gl.glPointSize(2)

        self._solidsQueue.clear()
        self._transparentQueue.clear()
        self._overlayQueue.clear()

        self._render_selection = True

    def queueNode(self, node, **kwargs):
        queueItem = { 'node': node }

        if 'mesh' in kwargs:
            queueItem['mesh'] = kwargs['mesh']

        queueItem['material'] = kwargs.get('material', self._defaultMaterial)

        mode = kwargs.get('mode', Renderer.RenderTriangles)
        if mode is Renderer.RenderLines:
            queueItem['mode'] = self._gl.GL_LINES
        elif mode is Renderer.RenderLineLoop:
            queueItem['mode'] = self._gl.GL_LINE_LOOP
        elif mode is Renderer.RenderPoints:
            queueItem['mode'] = self._gl.GL_POINTS
        else:
            queueItem['mode'] = self._gl.GL_TRIANGLES

        queueItem['wireframe'] = (mode == Renderer.RenderWireframe)

        if kwargs.get('transparent', False):
            self._transparentQueue.append(queueItem)
        elif kwargs.get('overlay', False):
            self._overlayQueue.append(queueItem)
        else:
            self._solidsQueue.append(queueItem)

    def renderQueuedNodes(self):
        self._gl.glEnable(self._gl.GL_DEPTH_TEST)
        self._gl.glDepthFunc(self._gl.GL_LESS)
        self._gl.glDepthMask(self._gl.GL_TRUE)
        self._gl.glDisable(self._gl.GL_CULL_FACE)

        self._scene.acquireLock()

        self._camera = self._scene.getActiveCamera()
        if not self._camera:
            Logger.log("e", "No active camera set, can not render")
            self._scene.releaseLock()
            return

        # Render the selection image
        selectable_nodes = []
        for node in DepthFirstIterator(self._scene.getRoot()):
            if node.isSelectable() and node.getMeshData():
                selectable_nodes.append(node)
        if selectable_nodes:
            #TODO: Use a limited area around the mouse rather than a full viewport for rendering
            if self._selection_buffer.width() < self._viewportWidth or self._selection_buffer.height() < self._viewportHeight:
                self._selection_buffer = self.createFrameBuffer(self._viewportWidth, self._viewportHeight)

            self._selection_buffer.bind()
            self._gl.glClearColor(0.0, 0.0, 0.0, 0.0)
            self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
            self._gl.glDisable(self._gl.GL_BLEND)
            self._selection_map.clear()
            for node in selectable_nodes:
                if type(node) is PointCloudNode:
                    self._renderItem({
                        'node': node,
                        'material': self._handle_material,
                        'mode': self._gl.GL_POINTS
                    })
                else :
                    color = self._getObjectColor(node)
                    self._selection_map[color] = id(node)
                    self._selection_material.setUniformValue('u_color', color)
                    self._renderItem({
                        'node': node,
                        'material': self._selection_material,
                        'mode': self._gl.GL_TRIANGLES
                    })
            tool = self._controller.getActiveTool()
            if tool:
                toolHandle = tool.getHandle()
                if toolHandle:
                    self._selection_map.update(toolHandle.getSelectionMap())
                    self._gl.glDisable(self._gl.GL_DEPTH_TEST)
                    if toolHandle.getLineMesh():
                        self._gl.glLineWidth(5)
                        self._renderItem({
                            'node': toolHandle,
                            'mesh': toolHandle.getLineMesh(),
                            'material': self._handle_material,
                            'mode': self._gl.GL_LINES
                        })
                        self._gl.glLineWidth(1)

                    if toolHandle.getSolidMesh():
                        self._renderItem({
                            'node': toolHandle,
                            'mesh': toolHandle.getSolidMesh(),
                            'material': self._handle_material,
                            'mode': self._gl.GL_TRIANGLES
                        })
                    self._gl.glEnable(self._gl.GL_DEPTH_TEST)

            self._selection_buffer.release()
            self._selection_image = self._selection_buffer.toImage()

        self._gl.glEnable(self._gl.GL_STENCIL_TEST)
        self._gl.glStencilMask(0xff)
        self._gl.glClearStencil(0)
        self._gl.glClear(self._gl.GL_STENCIL_BUFFER_BIT)
        self._gl.glStencilFunc(self._gl.GL_ALWAYS, 0xff, 0xff)
        self._gl.glStencilOp(self._gl.GL_REPLACE, self._gl.GL_REPLACE, self._gl.GL_REPLACE)
        self._gl.glStencilMask(0)

        for item in self._solidsQueue:
            if Selection.isSelected(item['node']):
                self._gl.glStencilMask(0xff)
                self._renderItem(item)
                self._gl.glStencilMask(0)
            else:
                self._renderItem(item)

        if self._render_selection:
            self._gl.glStencilMask(0)
            self._gl.glStencilFunc(self._gl.GL_EQUAL, 0, 0xff)
            self._gl.glLineWidth(2)
            for node in Selection.getAllSelectedObjects():
                if node.getMeshData() and type(node) is not PointCloudNode:
                    self._renderItem({
                        'node': node,
                        'material': self._outline_material,
                        'mode': self._gl.GL_TRIANGLES,
                        'wireframe': True
                    })

            self._gl.glLineWidth(1)

        self._gl.glDisable(self._gl.GL_STENCIL_TEST)
        self._gl.glDepthMask(self._gl.GL_FALSE)
        self._gl.glEnable(self._gl.GL_BLEND)
        self._gl.glEnable(self._gl.GL_CULL_FACE)
        self._gl.glBlendFunc(self._gl.GL_SRC_ALPHA, self._gl.GL_ONE_MINUS_SRC_ALPHA)

        for item in self._transparentQueue:
            self._renderItem(item)

        self._gl.glDisable(self._gl.GL_DEPTH_TEST)
        self._gl.glDisable(self._gl.GL_CULL_FACE)

        for item in self._overlayQueue:
            self._renderItem(item)

        self._scene.releaseLock()

    def endRendering(self):
        pass

    def _initialize(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        self._gl.initializeOpenGLFunctions()

        self._defaultMaterial = self.createMaterial(
                                     Resources.getPath(Resources.ShadersLocation, 'default.vert'),
                                     Resources.getPath(Resources.ShadersLocation, 'default.frag')
                                )

        self._defaultMaterial.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
        self._defaultMaterial.setUniformValue("u_diffuseColor", Color(0.5, 0.5, 0.5, 1.0))
        self._defaultMaterial.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
        self._defaultMaterial.setUniformValue("u_shininess", 50.0)

        self._selection_buffer = self.createFrameBuffer(128, 128)
        self._selection_material = self.createMaterial(
                                        Resources.getPath(Resources.ShadersLocation, 'basic.vert'),
                                        Resources.getPath(Resources.ShadersLocation, 'color.frag')
                                   )

        self._handle_material = self.createMaterial(
                                     Resources.getPath(Resources.ShadersLocation, 'basic.vert'),
                                     Resources.getPath(Resources.ShadersLocation, 'vertexcolor.frag')
                                )

        self._outline_material = self.createMaterial(
                                      Resources.getPath(Resources.ShadersLocation, 'outline.vert'),
                                       Resources.getPath(Resources.ShadersLocation, 'outline.frag')
                                 )

        self._initialized = True

    def _renderItem(self, item):
        node = item['node']
        mesh = item.get('mesh', node.getMeshData())
        transform = node.getGlobalTransformation()
        material = item['material']
        mode = item['mode']
        wireframe = item.get('wireframe', False)

        material.bind()
        material.setUniformValue("u_projectionMatrix", self._camera.getProjectionMatrix(), cache = False)
        material.setUniformValue("u_viewMatrix", self._camera.getGlobalTransformation().getInverse(), cache = False)
        material.setUniformValue("u_viewPosition", self._camera.getGlobalPosition(), cache = False)
        material.setUniformValue("u_modelMatrix", transform, cache = False)
        material.setUniformValue("u_lightPosition", self._camera.getGlobalPosition(), cache = False)

        if mesh.hasNormals():
            normalMatrix = transform
            normalMatrix.setRow(3, [0, 0, 0, 1])
            normalMatrix.setColumn(3, [0, 0, 0, 1])
            normalMatrix = normalMatrix.getInverse().getTransposed()
            material.setUniformValue("u_normalMatrix", normalMatrix, cache = False)

        try:
            vertexBuffer = getattr(mesh, vertexBufferProperty)
        except AttributeError:
            vertexBuffer =  self._createVertexBuffer(mesh)
        vertexBuffer.bind()

        if mesh.hasIndices():
            try:
                indexBuffer = getattr(mesh, indexBufferProperty)
            except AttributeError:
                indexBuffer = self._createIndexBuffer(mesh)
            indexBuffer.bind()

        material.enableAttribute("a_vertex", 'vector3f', 0)
        offset = mesh.getVertexCount() * 3 * 4

        if mesh.hasNormals():
            material.enableAttribute("a_normal", 'vector3f', offset)
            offset += mesh.getVertexCount() * 3 * 4

        if mesh.hasColors():
            material.enableAttribute("a_color", 'vector4f', offset)
            offset += mesh.getVertexCount() * 4 * 4

        if mesh.hasUVCoordinates():
            material.enableAttribute("a_uvs", 'vector2f', offset)
            offset += mesh.getVertexCount() * 2 * 4

        if wireframe and hasattr(self._gl, 'glPolygonMode'):
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_LINE)

        if mesh.hasIndices():
            if mode == self._gl.GL_TRIANGLES:
                self._gl.glDrawElements(mode, mesh.getFaceCount() * 3 , self._gl.GL_UNSIGNED_INT, None)
            else:
                self._gl.glDrawElements(mode, mesh.getFaceCount(), self._gl.GL_UNSIGNED_INT, None)
        else:
            self._gl.glDrawArrays(mode, 0, mesh.getVertexCount())

        if wireframe and hasattr(self._gl, 'glPolygonMode'):
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_FILL)

        material.disableAttribute("a_vertex")
        material.disableAttribute("a_normal")
        material.disableAttribute("a_color")
        material.disableAttribute("a_uvs")
        vertexBuffer.release()

        if mesh.hasIndices():
            indexBuffer.release()

        material.release()

    def _createVertexBuffer(self, mesh):
        buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        buffer.create()
        buffer.bind()

        bufferSize = mesh.getVertexCount() * 3 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasNormals():
            bufferSize += mesh.getVertexCount() * 3 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasColors():
            bufferSize += mesh.getVertexCount() * 4 * 4 # Vertex count * number of components * sizeof(float32)
        if mesh.hasUVCoordinates():
            bufferSize += mesh.getVertexCount() * 2 * 4 # Vertex count * number of components * sizeof(float32)

        buffer.allocate(bufferSize)

        offset = 0
        vertices = mesh.getVerticesAsByteArray()
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

    def _getObjectColor(self, node):
        obj_id = id(node)
        r = (obj_id & 0xff000000) >> 24
        g = (obj_id & 0x00ff0000) >> 16
        b = (obj_id & 0x0000ff00) >> 8
        a = (obj_id & 0x000000ff) >> 0
        return Color(r, g, b, a)
