# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Signal import Signal, SignalEmitter
from UM.Job import Job
from UM.Mesh.MeshData import MeshData
from UM.Logger import Logger
from copy import copy, deepcopy

import math

##  A scene node object.
#
#   These objects can hold a mesh and multiple children. Each node has a transformation matrix
#   that maps it it's parents space to the local space (it's inverse maps local space to parent).
#
#   \todo Add unit testing
class SceneNode(SignalEmitter):
    class TransformSpace:
        Local = 1
        Parent = 2
        World = 3

    def __init__(self, parent = None, **kwargs):
        super().__init__() # Call super to make multiple inheritence work.

        self._children = []
        self._mesh_data = None

        self._position = Vector()
        self._scale = Vector(1.0, 1.0, 1.0)
        self._shear = Vector(0.0, 0.0, 0.0)
        self._orientation = Quaternion()

        self._transformation = Matrix() #local transformation
        self._world_transformation = Matrix()

        self._derived_position = Vector()
        self._derived_orientation = Quaternion()
        self._derived_scale = Vector()

        self._inherit_orientation = True
        self._inherit_scale = True

        self._parent = parent
        self._enabled = True
        self._selectable = False
        self._calculate_aabb = True
        self._aabb = None
        self._aabb_job = None
        self._visible = kwargs.get("visible", True)
        self._name = kwargs.get("name", "")
        self._decorators = []
        self._bounding_box_mesh = None
        self.boundingBoxChanged.connect(self.calculateBoundingBoxMesh)
        self.parentChanged.connect(self._onParentChanged)

        if parent:
            parent.addChild(self)

    def __deepcopy__(self, memo):
        copy = SceneNode()
        copy.translate(self.getPosition())
        copy.setOrientation(self.getOrientation())
        copy.setScale(self.getScale())
        copy.setMeshData(deepcopy(self._mesh_data, memo))
        copy.setVisible(deepcopy(self._visible, memo))
        copy._selectable = deepcopy(self._selectable, memo)
        for decorator in self._decorators:
            copy.addDecorator(deepcopy(decorator, memo))

        for child in self._children:
            copy.addChild(deepcopy(child, memo))
        self.calculateBoundingBoxMesh()
        return copy

    def setCenterPosition(self, center):
        if self._mesh_data:
            m = Matrix()
            m.setByTranslation(-center)
            self._mesh_data = self._mesh_data.getTransformed(m)
            self._mesh_data.setCenterPosition(center)
        for child in self._children:
            child.setCenterPosition(center)

    ##  \brief Get the parent of this node. If the node has no parent, it is the root node.
    #   \returns SceneNode if it has a parent and None if it's the root node.
    def getParent(self):
        return self._parent

    def getBoundingBoxMesh(self):
        return self._bounding_box_mesh

    def calculateBoundingBoxMesh(self):
        if self._aabb:
            self._bounding_box_mesh = MeshData()
            rtf = self._aabb.maximum
            lbb = self._aabb.minimum

            self._bounding_box_mesh.addVertex(rtf.x, rtf.y, rtf.z) #Right - Top - Front
            self._bounding_box_mesh.addVertex(lbb.x, rtf.y, rtf.z) #Left - Top - Front

            self._bounding_box_mesh.addVertex(lbb.x, rtf.y, rtf.z) #Left - Top - Front
            self._bounding_box_mesh.addVertex(lbb.x, lbb.y, rtf.z) #Left - Bottom - Front

            self._bounding_box_mesh.addVertex(lbb.x, lbb.y, rtf.z) #Left - Bottom - Front
            self._bounding_box_mesh.addVertex(rtf.x, lbb.y, rtf.z) #Right - Bottom - Front

            self._bounding_box_mesh.addVertex(rtf.x, lbb.y, rtf.z) #Right - Bottom - Front
            self._bounding_box_mesh.addVertex(rtf.x, rtf.y, rtf.z) #Right - Top - Front

            self._bounding_box_mesh.addVertex(rtf.x, rtf.y, lbb.z) #Right - Top - Back
            self._bounding_box_mesh.addVertex(lbb.x, rtf.y, lbb.z) #Left - Top - Back

            self._bounding_box_mesh.addVertex(lbb.x, rtf.y, lbb.z) #Left - Top - Back
            self._bounding_box_mesh.addVertex(lbb.x, lbb.y, lbb.z) #Left - Bottom - Back

            self._bounding_box_mesh.addVertex(lbb.x, lbb.y, lbb.z) #Left - Bottom - Back
            self._bounding_box_mesh.addVertex(rtf.x, lbb.y, lbb.z) #Right - Bottom - Back

            self._bounding_box_mesh.addVertex(rtf.x, lbb.y, lbb.z) #Right - Bottom - Back
            self._bounding_box_mesh.addVertex(rtf.x, rtf.y, lbb.z) #Right - Top - Back

            self._bounding_box_mesh.addVertex(rtf.x, rtf.y, rtf.z) #Right - Top - Front
            self._bounding_box_mesh.addVertex(rtf.x, rtf.y, lbb.z) #Right - Top - Back

            self._bounding_box_mesh.addVertex(lbb.x, rtf.y, rtf.z) #Left - Top - Front
            self._bounding_box_mesh.addVertex(lbb.x, rtf.y, lbb.z) #Left - Top - Back

            self._bounding_box_mesh.addVertex(lbb.x, lbb.y, rtf.z) #Left - Bottom - Front
            self._bounding_box_mesh.addVertex(lbb.x, lbb.y, lbb.z) #Left - Bottom - Back

            self._bounding_box_mesh.addVertex(rtf.x, lbb.y, rtf.z) #Right - Bottom - Front
            self._bounding_box_mesh.addVertex(rtf.x, lbb.y, lbb.z) #Right - Bottom - Back
        else:
            self._resetAABB()

    def _onParentChanged(self, node):
        for child in self.getChildren():
            child.parentChanged.emit(self)

    decoratorsChanged = Signal()
    
    def addDecorator(self, decorator):
        decorator.setNode(self)
        self._decorators.append(decorator)
        self.decoratorsChanged.emit(self)

    def getDecorators(self):
        return self._decorators

    def getDecorator(self, dec_type):
        for decorator in self._decorators:
            if type(decorator) == dec_type:
                return decorator

    def removeDecorators(self):
        self._decorators = []
        self.decoratorsChanged.emit(self)

    def removeDecorator(self, dec_type):
        for decorator in self._decorators:
            if type(decorator) == dec_type:
                self._decorators.remove(decorator)
                self.decoratorsChanged.emit(self)
                break

    def callDecoration(self, function, *args, **kwargs):
        for decorator in self._decorators:
            if hasattr(decorator, function):
                try:
                    return getattr(decorator, function)(*args, **kwargs)
                except Exception as e:
                    Logger.log("e", "Exception calling decoration %s: %s", str(function), str(e))
                    return None

    def hasDecoration(self, function):
        for decorator in self._decorators:
            if hasattr(decorator, function):
                return True
        return False

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    ##  How many nodes is this node removed from the root
    def getDepth(self):
        if self._parent is None:
            return 0
        return self._parent.getDepth() + 1

    ##  \brief Set the parent of this object
    #   \param scene_node SceneNode that is the parent of this object.
    def setParent(self, scene_node):
        if self._parent:
            self._parent.removeChild(self)
        #self._parent = scene_node

        if scene_node:
            scene_node.addChild(self)

    ##  Emitted whenever the parent changes.
    parentChanged = Signal()

    ##  \brief Get the visibility of this node. The parents visibility overrides the visibility.
    #   TODO: Let renderer actually use the visibility to decide wether to render or not.
    def isVisible(self):
        if self._parent != None and self._visible:
            return self._parent.isVisible()
        else:
            return self._visible

    def setVisible(self, visible):
        self._visible = visible

    ##  \brief Get the (original) mesh data from the scene node/object.
    #   \returns MeshData
    def getMeshData(self):
        return self._mesh_data

    ##  \brief Get the transformed mesh data from the scene node/object, based on the transformation of scene nodes wrt root.
    #   \returns MeshData
    def getMeshDataTransformed(self):
        #transformed_mesh = deepcopy(self._mesh_data)
        #transformed_mesh.transform(self.getWorldTransformation())
        return self._mesh_data.getTransformed(self.getWorldTransformation())

    ##  \brief Set the mesh of this node/object
    #   \param mesh_data MeshData object
    def setMeshData(self, mesh_data):
        if self._mesh_data:
            self._mesh_data.dataChanged.disconnect(self._onMeshDataChanged)
        self._mesh_data = mesh_data
        if self._mesh_data is not None:
            self._mesh_data.dataChanged.connect(self._onMeshDataChanged)
        self._resetAABB()
        self.meshDataChanged.emit(self)

    ##  Emitted whenever the attached mesh data object changes.
    meshDataChanged = Signal()

    def _onMeshDataChanged(self):
        self.meshDataChanged.emit(self)

    ##  \brief Add a child to this node and set it's parent as this node.
    #   \params scene_node SceneNode to add.
    def addChild(self, scene_node):
        if scene_node not in self._children:
            scene_node.transformationChanged.connect(self.transformationChanged)
            scene_node.childrenChanged.connect(self.childrenChanged)
            scene_node.meshDataChanged.connect(self.meshDataChanged)

            self._children.append(scene_node)
            self._resetAABB()
            self.childrenChanged.emit(self)

            if not scene_node._parent is self:
                scene_node._parent = self
                scene_node._transformChanged()
                scene_node.parentChanged.emit(self)

    ##  \brief remove a single child
    #   \param child Scene node that needs to be removed.
    def removeChild(self, child):
        if child not in self._children:
            return

        child.transformationChanged.disconnect(self.transformationChanged)
        child.childrenChanged.disconnect(self.childrenChanged)
        child.meshDataChanged.disconnect(self.meshDataChanged)

        self._children.remove(child)
        child._parent = None
        child._transformChanged()
        child.parentChanged.emit(self)

        self.childrenChanged.emit(self)

    ##  \brief Removes all children and its children's children.
    def removeAllChildren(self):
        for child in self._children:
            child.removeAllChildren()
            self.removeChild(child)

        self.childrenChanged.emit(self)

    ##  \brief Get the list of direct children
    #   \returns List of children
    def getChildren(self):
        return self._children

    def hasChildren(self):
        return True if self._children else False

    ##  \brief Get list of all children (including it's children children children etc.)
    #   \returns list ALl children in this 'tree'
    def getAllChildren(self):
        children = []
        children.extend(self._children)
        for child in self._children:
            children.extend(child.getAllChildren())
        return children

    ##  \brief Emitted whenever the list of children of this object or any child object changes.
    #   \param object The object that triggered the change.
    childrenChanged = Signal()

    ##  \brief Computes and returns the transformation from world to local space.
    #   \returns 4x4 transformation matrix
    def getWorldTransformation(self):
        if self._world_transformation is None:
            self._updateTransformation()

        return deepcopy(self._world_transformation)

    ##  \brief Returns the local transformation with respect to its parent. (from parent to local)
    #   \retuns transformation 4x4 (homogenous) matrix
    def getLocalTransformation(self):
        if self._transformation is None:
            self._updateTransformation()

        return deepcopy(self._transformation)

    def setTransformation(self, transformation):
        self._transformation = transformation
        self._transformChanged()

    ##  Get the local orientation value.
    def getOrientation(self):
        return deepcopy(self._orientation)

    def getWorldOrientation(self):
        return deepcopy(self._derived_orientation)

    ##  \brief Rotate the scene object (and thus its children) by given amount
    #
    #   \param rotation \type{Quaternion} A quaternion indicating the amount of rotation.
    #   \param transform_space The space relative to which to rotate. Can be any one of the constants in SceneNode::TransformSpace.
    def rotate(self, rotation, transform_space = TransformSpace.Local):
        if not self._enabled:
            return

        orientation_matrix = rotation.toMatrix()
        if transform_space == SceneNode.TransformSpace.Local:
            self._transformation.multiply(orientation_matrix)
        elif transform_space == SceneNode.TransformSpace.Parent:
            self._transformation.preMultiply(orientation_matrix)
        elif transform_space == SceneNode.TransformSpace.World:
            self._transformation.multiply(self._world_transformation.getInverse())
            self._transformation.multiply(orientation_matrix)
            self._transformation.multiply(self._world_transformation)

        self._transformChanged()

    ##  Set the local orientation of this scene node.
    #
    #   \param orientation \type{Quaternion} The new orientation of this scene node.
    #   \param transform_space The space relative to which to rotate. Can be Local or World from SceneNode::TransformSpace.
    def setOrientation(self, orientation, transform_space = TransformSpace.Local):
        if not self._enabled or orientation == self._orientation:
            return

        new_transform_matrix = Matrix()
        if transform_space == SceneNode.TransformSpace.Local:
            orientation_matrix = orientation.toMatrix()
        if transform_space == SceneNode.TransformSpace.World:
            if self.getWorldOrientation() == orientation:
                return
            new_orientation = orientation * (self.getWorldOrientation() * self._orientation.getInverse()).getInverse()
            orientation_matrix = new_orientation.toMatrix()
        euler_angles = orientation_matrix.getEuler()

        new_transform_matrix.compose(scale = self._scale, angles = euler_angles, translate = self._position, shear = self._shear)
        self._transformation = new_transform_matrix
        self._transformChanged()

    ##  Get the local scaling value.
    def getScale(self):
        return deepcopy(self._scale)

    def getWorldScale(self):
        return deepcopy(self._derived_scale)

    ##  Scale the scene object (and thus its children) by given amount
    #
    #   \param scale \type{Vector} A Vector with three scale values
    #   \param transform_space The space relative to which to scale. Can be any one of the constants in SceneNode::TransformSpace.
    def scale(self, scale, transform_space = TransformSpace.Local):
        if not self._enabled:
            return

        scale_matrix = Matrix()
        scale_matrix.setByScaleVector(scale)
        if transform_space == SceneNode.TransformSpace.Local:
            self._transformation.multiply(scale_matrix)
        elif transform_space == SceneNode.TransformSpace.Parent:
            self._transformation.preMultiply(scale_matrix)
        elif transform_space == SceneNode.TransformSpace.World:
            self._transformation.multiply(self._world_transformation.getInverse())
            self._transformation.multiply(scale_matrix)
            self._transformation.multiply(self._world_transformation)

        self._transformChanged()

    ##  Set the local scale value.
    #
    #   \param scale \type{Vector} The new scale value of the scene node.
    #   \param transform_space The space relative to which to rotate. Can be Local or World from SceneNode::TransformSpace.
    def setScale(self, scale, transform_space = TransformSpace.Local):
        if not self._enabled or scale == self._scale:
            return
        if transform_space == SceneNode.TransformSpace.Local:
            self.scale(scale / self._scale, SceneNode.TransformSpace.Local)
            return
        if transform_space == SceneNode.TransformSpace.World:
            if self.getWorldScale() == scale:
                return
            self.scale(scale / self._scale, SceneNode.TransformSpace.World)

    ##  Get the local position.
    def getPosition(self):
        return deepcopy(self._position)

    ##  Get the position of this scene node relative to the world.
    def getWorldPosition(self):
        return deepcopy(self._derived_position)

    ##  Translate the scene object (and thus its children) by given amount.
    #
    #   \param translation \type{Vector} The amount to translate by.
    #   \param transform_space The space relative to which to translate. Can be any one of the constants in SceneNode::TransformSpace.
    def translate(self, translation, transform_space = TransformSpace.Local):
        if not self._enabled:
            return
        translation_matrix = Matrix()
        translation_matrix.setByTranslation(translation)
        if transform_space == SceneNode.TransformSpace.Local:
            self._transformation.multiply(translation_matrix)
        elif transform_space == SceneNode.TransformSpace.Parent:
            self._transformation.preMultiply(translation_matrix)
        elif transform_space == SceneNode.TransformSpace.World:
            self._transformation.multiply(self._world_transformation.getInverse())
            self._transformation.multiply(translation_matrix)
            self._transformation.multiply(self._world_transformation)
        self._transformChanged()

    ##  Set the local position value.
    #
    #   \param position The new position value of the SceneNode.
    #   \param transform_space The space relative to which to rotate. Can be Local or World from SceneNode::TransformSpace.
    def setPosition(self, position, transform_space = TransformSpace.Local):
        if not self._enabled or position == self._position:
            return
        if transform_space == SceneNode.TransformSpace.Local:
            self.translate(position - self._position, SceneNode.TransformSpace.Parent)
        if transform_space == SceneNode.TransformSpace.World:
            if self.getWorldPosition() == position:
                return
            self.translate(position - self._position, SceneNode.TransformSpace.World)

    ##  Signal. Emitted whenever the transformation of this object or any child object changes.
    #   \param object The object that caused the change.
    transformationChanged = Signal()

    ##  Rotate this scene node in such a way that it is looking at target.
    #
    #   \param target \type{Vector} The target to look at.
    #   \param up \type{Vector} The vector to consider up. Defaults to Vector.Unit_Y, i.e. (0, 1, 0).
    def lookAt(self, target, up = Vector.Unit_Y):
        if not self._enabled:
            return

        eye = self.getWorldPosition()
        f = (target - eye).normalize()
        up.normalize()
        s = f.cross(up).normalize()
        u = s.cross(f).normalize()

        m = Matrix([
            [ s.x,  u.x,  -f.x, 0.0],
            [ s.y,  u.y,  -f.y, 0.0],
            [ s.z,  u.z,  -f.z, 0.0],
            [ 0.0,  0.0,  0.0,  1.0]
        ])


        self.setOrientation(Quaternion.fromMatrix(m))

    ##  Can be overridden by child nodes if they need to perform special rendering.
    #   If you need to handle rendering in a special way, for example for tool handles,
    #   you can override this method and render the node. Return True to prevent the
    #   view from rendering any attached mesh data.
    #
    #   \param renderer The renderer object to use for rendering.
    #
    #   \return False if the view should render this node, True if we handle our own rendering.
    def render(self, renderer):
        return False

    ##  Get whether this SceneNode is enabled, that is, it can be modified in any way.
    def isEnabled(self):
        if self._parent != None and self._enabled:
            return self._parent.isEnabled()
        else:
            return self._enabled

    ##  Set whether this SceneNode is enabled.
    #   \param enable True if this object should be enabled, False if not.
    #   \sa isEnabled
    def setEnabled(self, enable):
        self._enabled = enable

    ##  Get whether this SceneNode can be selected.
    #
    #   \note This will return false if isEnabled() returns false.
    def isSelectable(self):
        return self._enabled and self._selectable

    ##  Set whether this SceneNode can be selected.
    #
    #   \param select True if this SceneNode should be selectable, False if not.
    def setSelectable(self, select):
        self._selectable = select

    ##  Get the bounding box of this node and its children.
    #
    #   Note that the AABB is calculated in a separate thread. This method will return an invalid (size 0) AABB
    #   while the calculation happens.
    def getBoundingBox(self):
        if self._aabb:
            return self._aabb

        if not self._aabb_job:
            self._resetAABB()

        return AxisAlignedBox()

    ##  Set whether or not to calculate the bounding box for this node.
    #
    #   \param calculate True if the bounding box should be calculated, False if not.
    def setCalculateBoundingBox(self, calculate):
        self._calculate_aabb = calculate

    boundingBoxChanged = Signal()

    ##  private:
    def _transformChanged(self):
        self._updateTransformation()
        self._resetAABB()
        self.transformationChanged.emit(self)

        for child in self._children:
            child._transformChanged()

    def _updateTransformation(self):
        scale, shear, euler_angles, translation = self._transformation.decompose()
        self._position = translation
        self._scale = scale
        self._shear = shear
        orientation = Quaternion()
        euler_angle_matrix = Matrix()
        euler_angle_matrix.setByEuler(euler_angles.x, euler_angles.y, euler_angles.z)
        orientation.setByMatrix(euler_angle_matrix)
        self._orientation = orientation
        if self._parent:
            self._world_transformation = self._parent.getWorldTransformation().multiply(self._transformation, copy = True)
        else:
            self._world_transformation = self._transformation

        world_scale, world_shear, world_euler_angles, world_translation = self._world_transformation.decompose()
        self._derived_position = world_translation
        self._derived_scale = world_scale

        world_euler_angle_matrix = Matrix()
        world_euler_angle_matrix.setByEuler(world_euler_angles.x, world_euler_angles.y, world_euler_angles.z)
        self._derived_orientation.setByMatrix(world_euler_angle_matrix)

        world_scale, world_shear, world_euler_angles, world_translation = self._world_transformation.decompose()

    def _resetAABB(self):
        if not self._calculate_aabb:
            return

        self._aabb = None

        if self._aabb_job:
            self._aabb_job.cancel()

        self._aabb_job = _CalculateAABBJob(self)
        self._aabb_job.start()

##  Internal
#   Calculates the AABB of a node and its children.
class _CalculateAABBJob(Job):
    def __init__(self, node):
        super().__init__()
        self._node = node

    def run(self):
        aabb = None
        if self._node._mesh_data:
            aabb = self._node._mesh_data.getExtents(self._node.getWorldTransformation())
        else:
            aabb = None

        for child in self._node._children:
            if aabb is None:
                aabb = deepcopy(child.getBoundingBox())
            else:
                aabb += child.getBoundingBox()

        self._node._aabb = aabb
        self._node._aabb_job = None
        if self._node.getParent():
            self._node.getParent()._resetAABB()

        self._node.boundingBoxChanged.emit()
