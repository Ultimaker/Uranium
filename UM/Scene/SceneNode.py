# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from copy import deepcopy
from typing import Any, Dict, List, Optional, cast

import numpy

from UM.Logger import Logger
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Matrix import Matrix
from UM.Math.Quaternion import Quaternion
from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData
from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from UM.Signal import Signal, signalemitter


@signalemitter
class SceneNode:
    """A scene node object.

    These objects can hold a mesh and multiple children. Each node has a transformation matrix
    that maps it it's parents space to the local space (it's inverse maps local space to parent).

    SceneNodes can be "Decorated" by adding SceneNodeDecorator objects.
    These decorators can add functionality to scene nodes.
    :sa SceneNodeDecorator
    :todo Add unit testing
    """

    class TransformSpace:
        Local = 1 #type: int
        Parent = 2 #type: int
        World = 3 #type: int

    def __init__(self, parent: Optional["SceneNode"] = None, visible: bool = True, name: str = "", node_id: str = "") -> None:
        """Construct a scene node.

        :param parent: The parent of this node (if any). Only a root node should have None as a parent.
        :param visible: Is the SceneNode (and thus, all its children) visible?
        :param name: Name of the SceneNode.
        """

        super().__init__()  # Call super to make multiple inheritance work.

        self._children = []     # type: List[SceneNode]
        self._mesh_data = None  # type: Optional[MeshData]

        # Local transformation (from parent to local)
        self._transformation = Matrix()  # type: Matrix

        # Convenience "components" of the transformation
        self._position = Vector()  # type: Vector
        self._scale = Vector(1.0, 1.0, 1.0)  # type: Vector
        self._shear = Vector(0.0, 0.0, 0.0)  # type: Vector
        self._mirror = Vector(1.0, 1.0, 1.0)  # type: Vector
        self._orientation = Quaternion()  # type: Quaternion

        # World transformation (from root to local)
        self._world_transformation = Matrix()  # type: Matrix

        # This is used for rendering. Since we don't want to recompute it every time, we cache it in the node
        self._cached_normal_matrix = Matrix()

        # Convenience "components" of the world_transformation
        self._derived_position = Vector()  # type: Vector
        self._derived_orientation = Quaternion()  # type: Quaternion
        self._derived_scale = Vector()  # type: Vector

        self._parent = parent  # type: Optional[SceneNode]

        # Can this SceneNode be modified in any way?
        self._enabled = True  # type: bool
        # Can this SceneNode be selected in any way?
        self._selectable = False  # type: bool

        # Should the AxisAlignedBoundingBox be re-calculated?
        self._calculate_aabb = True  # type: bool

        # The AxisAligned bounding box.
        self._aabb = None  # type: Optional[AxisAlignedBox]
        self._bounding_box_mesh = None  # type: Optional[MeshData]

        self._visible = visible  # type: bool
        self._name = name  # type: str
        self._id = node_id  # type: str
        self._decorators = []  # type: List[SceneNodeDecorator]

        # Store custom settings to be compatible with Savitar SceneNode
        self._settings = {}  # type: Dict[str, Any]

        ## Signals
        self.parentChanged.connect(self._onParentChanged)

        if parent:
            parent.addChild(self)

    def __deepcopy__(self, memo: Dict[int, object]) -> "SceneNode":
        copy = self.__class__()
        copy.setTransformation(self.getLocalTransformation())
        copy.setMeshData(self._mesh_data)
        copy._visible = cast(bool, deepcopy(self._visible, memo))
        copy._selectable = cast(bool, deepcopy(self._selectable, memo))
        copy._name = cast(str, deepcopy(self._name, memo))
        for decorator in self._decorators:
            copy.addDecorator(cast(SceneNodeDecorator, deepcopy(decorator, memo)))

        for child in self._children:
            copy.addChild(cast(SceneNode, deepcopy(child, memo)))
        self.calculateBoundingBoxMesh()
        return copy

    def setCenterPosition(self, center: Vector) -> None:
        """Set the center position of this node.

        This is used to modify it's mesh data (and it's children) in such a way that they are centered.
        In most cases this means that we use the center of mass as center (which most objects don't use)
        """

        if self._mesh_data:
            m = Matrix()
            m.setByTranslation(-center)
            self._mesh_data = self._mesh_data.getTransformed(m).set(center_position=center)
        for child in self._children:
            child.setCenterPosition(center)

    def getParent(self) -> Optional["SceneNode"]:
        """Get the parent of this node.

        If the node has no parent, it is the root node.

        :returns: SceneNode if it has a parent and None if it's the root node.
        """

        return self._parent

    def getMirror(self) -> Vector:
        return self._mirror

    def setMirror(self, vector) -> None:
        self._mirror = vector

    def getBoundingBoxMesh(self) -> Optional[MeshData]:
        """Get the MeshData of the bounding box

        :returns: :type{MeshData} Bounding box mesh.
        """

        if self._bounding_box_mesh is None:
            self.calculateBoundingBoxMesh()
        return self._bounding_box_mesh

    def calculateBoundingBoxMesh(self) -> None:
        """(re)Calculate the bounding box mesh."""

        aabb = self.getBoundingBox()
        if aabb:
            bounding_box_mesh = MeshBuilder()
            rtf = aabb.maximum
            lbb = aabb.minimum

            bounding_box_mesh.addVertex(rtf.x, rtf.y, rtf.z)  # Right - Top - Front
            bounding_box_mesh.addVertex(lbb.x, rtf.y, rtf.z)  # Left - Top - Front

            bounding_box_mesh.addVertex(lbb.x, rtf.y, rtf.z)  # Left - Top - Front
            bounding_box_mesh.addVertex(lbb.x, lbb.y, rtf.z)  # Left - Bottom - Front

            bounding_box_mesh.addVertex(lbb.x, lbb.y, rtf.z)  # Left - Bottom - Front
            bounding_box_mesh.addVertex(rtf.x, lbb.y, rtf.z)  # Right - Bottom - Front

            bounding_box_mesh.addVertex(rtf.x, lbb.y, rtf.z)  # Right - Bottom - Front
            bounding_box_mesh.addVertex(rtf.x, rtf.y, rtf.z)  # Right - Top - Front

            bounding_box_mesh.addVertex(rtf.x, rtf.y, lbb.z)  # Right - Top - Back
            bounding_box_mesh.addVertex(lbb.x, rtf.y, lbb.z)  # Left - Top - Back

            bounding_box_mesh.addVertex(lbb.x, rtf.y, lbb.z)  # Left - Top - Back
            bounding_box_mesh.addVertex(lbb.x, lbb.y, lbb.z)  # Left - Bottom - Back

            bounding_box_mesh.addVertex(lbb.x, lbb.y, lbb.z)  # Left - Bottom - Back
            bounding_box_mesh.addVertex(rtf.x, lbb.y, lbb.z)  # Right - Bottom - Back

            bounding_box_mesh.addVertex(rtf.x, lbb.y, lbb.z)  # Right - Bottom - Back
            bounding_box_mesh.addVertex(rtf.x, rtf.y, lbb.z)  # Right - Top - Back

            bounding_box_mesh.addVertex(rtf.x, rtf.y, rtf.z)  # Right - Top - Front
            bounding_box_mesh.addVertex(rtf.x, rtf.y, lbb.z)  # Right - Top - Back

            bounding_box_mesh.addVertex(lbb.x, rtf.y, rtf.z)  # Left - Top - Front
            bounding_box_mesh.addVertex(lbb.x, rtf.y, lbb.z)  # Left - Top - Back

            bounding_box_mesh.addVertex(lbb.x, lbb.y, rtf.z)  # Left - Bottom - Front
            bounding_box_mesh.addVertex(lbb.x, lbb.y, lbb.z)  # Left - Bottom - Back

            bounding_box_mesh.addVertex(rtf.x, lbb.y, rtf.z)  # Right - Bottom - Front
            bounding_box_mesh.addVertex(rtf.x, lbb.y, lbb.z)  # Right - Bottom - Back

            self._bounding_box_mesh = bounding_box_mesh.build()

    def collidesWithBbox(self, check_bbox: AxisAlignedBox) -> bool:
        """Return if the provided bbox collides with the bbox of this SceneNode"""

        bbox = self.getBoundingBox()
        if bbox is not None:
            if check_bbox.intersectsBox(bbox) != AxisAlignedBox.IntersectionResult.FullIntersection:
                return True

        return False

    def _onParentChanged(self, node: Optional["SceneNode"]) -> None:
        """Handler for the ParentChanged signal
        :param node: Node from which this event was triggered.
        """

        for child in self.getChildren():
            child.parentChanged.emit(self)

    decoratorsChanged = Signal()
    """Signal for when a :type{SceneNodeDecorator} is added / removed."""

    def addDecorator(self, decorator: SceneNodeDecorator) -> None:
        """Add a SceneNodeDecorator to this SceneNode.

        :param decorator: The decorator to add.
        """

        if type(decorator) in [type(dec) for dec in self._decorators]:
            Logger.log("w", "Unable to add the same decorator type (%s) to a SceneNode twice.", type(decorator))
            return
        try:
            decorator.setNode(self)
        except AttributeError:
            Logger.logException("e", "Unable to add decorator.")
            return
        self._decorators.append(decorator)
        self.decoratorsChanged.emit(self)

    def getDecorators(self) -> List[SceneNodeDecorator]:
        """Get all SceneNodeDecorators that decorate this SceneNode.

        :return: list of all SceneNodeDecorators.
        """

        return self._decorators

    def getDecorator(self, dec_type: type) -> Optional[SceneNodeDecorator]:
        """Get SceneNodeDecorators by type.

        :param dec_type: type of decorator to return.
        """

        for decorator in self._decorators:
            if type(decorator) == dec_type:
                return decorator
        return None

    def removeDecorators(self):
        """Remove all decorators"""

        for decorator in self._decorators:
            decorator.clear()
        self._decorators = []
        self.decoratorsChanged.emit(self)

    def removeDecorator(self, dec_type: type) -> None:
        """Remove decorator by type.

        :param dec_type: type of the decorator to remove.
        """

        for decorator in self._decorators:
            if type(decorator) == dec_type:
                decorator.clear()
                self._decorators.remove(decorator)
                self.decoratorsChanged.emit(self)
                break

    def callDecoration(self, function: str, *args, **kwargs) -> Any:
        """Call a decoration of this SceneNode.

        SceneNodeDecorators add Decorations, which are callable functions.
        :param function: The function to be called.
        :param *args
        :param **kwargs
        """

        for decorator in self._decorators:
            if hasattr(decorator, function):
                try:
                    return getattr(decorator, function)(*args, **kwargs)
                except Exception as e:
                    Logger.logException("e", "Exception calling decoration %s: %s", str(function), str(e))
                    return None

    def hasDecoration(self, function: str) -> bool:
        """Does this SceneNode have a certain Decoration (as defined by a Decorator)
        :param :type{string} function the function to check for.
        """

        for decorator in self._decorators:
            if hasattr(decorator, function):
                return True
        return False

    def getName(self) -> str:
        return self._name

    def setName(self, name: str) -> None:
        self._name = name

    def getId(self) -> str:
        return self._id

    def setId(self, node_id: str) -> None:
        self._id = node_id

    def getDepth(self) -> int:
        """How many nodes is this node removed from the root?

        :return: Steps from root (0 means it -is- the root).
        """

        if self._parent is None:
            return 0
        return self._parent.getDepth() + 1

    def setParent(self, scene_node: Optional["SceneNode"]) -> None:
        """:brief Set the parent of this object

        :param scene_node: SceneNode that is the parent of this object.
        """

        if self._parent:
            self._parent.removeChild(self)

        if scene_node:
            scene_node.addChild(self)

    parentChanged = Signal()
    """Emitted whenever the parent changes."""

    def isVisible(self) -> bool:
        """Get the visibility of this node.
        The parents visibility overrides the visibility.
        TODO: Let renderer actually use the visibility to decide whether to render or not.
        """

        if self._parent is not None and self._visible:
            return self._parent.isVisible()
        else:
            return self._visible

    def setVisible(self, visible: bool) -> None:
        """Set the visibility of this SceneNode."""

        self._visible = visible

    def getMeshData(self) -> Optional[MeshData]:
        """Get the (original) mesh data from the scene node/object.

        :returns: MeshData
        """

        return self._mesh_data

    def getMeshDataTransformed(self) -> Optional[MeshData]:
        """Get the transformed mesh data from the scene node/object, based on the transformation of scene nodes wrt root.

        If this node is a group, it will recursively concatenate all child nodes/objects.
        :returns: MeshData
        """

        return MeshData(vertices = self.getMeshDataTransformedVertices(), normals = self.getMeshDataTransformedNormals())

    def getMeshDataTransformedVertices(self) -> numpy.ndarray:
        """Get the transformed vertices from this scene node/object, based on the transformation of scene nodes wrt root.

        If this node is a group, it will recursively concatenate all child nodes/objects.
        :return: numpy.ndarray
        """

        transformed_vertices = None
        if self.callDecoration("isGroup"):
            for child in self._children:
                tv = child.getMeshDataTransformedVertices()
                if transformed_vertices is None:
                    transformed_vertices = tv
                else:
                    transformed_vertices = numpy.concatenate((transformed_vertices, tv), axis = 0)
        else:
            if self._mesh_data:
                transformed_vertices = self._mesh_data.getTransformed(self.getWorldTransformation(copy=False)).getVertices()
        return transformed_vertices

    def getMeshDataTransformedNormals(self) -> numpy.ndarray:
        """Get the transformed normals from this scene node/object, based on the transformation of scene nodes wrt root.

        If this node is a group, it will recursively concatenate all child nodes/objects.
        :return: numpy.ndarray
        """

        transformed_normals = None
        if self.callDecoration("isGroup"):
            for child in self._children:
                tv = child.getMeshDataTransformedNormals()
                if transformed_normals is None:
                    transformed_normals = tv
                else:
                    transformed_normals = numpy.concatenate((transformed_normals, tv), axis = 0)
        else:
            if self._mesh_data:
                transformed_normals = self._mesh_data.getTransformed(self.getWorldTransformation(copy = False)).getNormals()
        return transformed_normals

    def setMeshData(self, mesh_data: Optional[MeshData]) -> None:
        """Set the mesh of this node/object

        :param mesh_data: MeshData object
        """

        self._mesh_data = mesh_data
        self._resetAABB()
        self.meshDataChanged.emit(self)

    meshDataChanged = Signal()
    """Emitted whenever the attached mesh data object changes."""

    def _onMeshDataChanged(self) -> None:
        self.meshDataChanged.emit(self)

    def addChild(self, scene_node: "SceneNode") -> None:
        """Add a child to this node and set it's parent as this node.

        :params scene_node SceneNode to add.
        """

        if scene_node in self._children:
            return

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

    def removeChild(self, child: "SceneNode") -> None:
        """remove a single child

        :param child: Scene node that needs to be removed.
        """

        if child not in self._children:
            return

        child.transformationChanged.disconnect(self.transformationChanged)
        child.childrenChanged.disconnect(self.childrenChanged)
        child.meshDataChanged.disconnect(self.meshDataChanged)

        self._children.remove(child)
        child._parent = None
        child._transformChanged()
        child.parentChanged.emit(self)

        self._resetAABB()
        self.childrenChanged.emit(self)

    def removeAllChildren(self) -> None:
        """Removes all children and its children's children."""

        for child in self._children:
            child.removeAllChildren()
            self.removeChild(child)

        self.childrenChanged.emit(self)

    def getChildren(self) -> List["SceneNode"]:
        """Get the list of direct children

        :returns: List of children
        """

        return self._children

    def hasChildren(self) -> bool:
        return True if self._children else False

    def getAllChildren(self) -> List["SceneNode"]:
        """Get list of all children (including it's children children children etc.)

        :returns: list ALl children in this 'tree'
        """

        children = []
        children.extend(self._children)
        for child in self._children:
            children.extend(child.getAllChildren())
        return children

    childrenChanged = Signal()
    """Emitted whenever the list of children of this object or any child object changes.

    :param object: The object that triggered the change.
    """

    def _updateCachedNormalMatrix(self) -> None:
        self._cached_normal_matrix = Matrix(self.getWorldTransformation(copy=False).getData())
        self._cached_normal_matrix.setRow(3, [0, 0, 0, 1])
        self._cached_normal_matrix.setColumn(3, [0, 0, 0, 1])
        self._cached_normal_matrix.invert()
        self._cached_normal_matrix.transpose()

    def getCachedNormalMatrix(self) -> Matrix:
        if self._cached_normal_matrix is None:
            self._updateCachedNormalMatrix()
        return self._cached_normal_matrix

    def getWorldTransformation(self, copy = True) -> Matrix:
        """Computes and returns the transformation from world to local space.

        :returns: 4x4 transformation matrix
        """

        if self._world_transformation is None:
            self._updateWorldTransformation()
        if copy:
            return self._world_transformation.copy()
        return self._world_transformation

    def getLocalTransformation(self, copy = True) -> Matrix:
        """Returns the local transformation with respect to its parent. (from parent to local)

        :returns transformation 4x4 (homogeneous) matrix
        """

        if self._transformation is None:
            self._updateLocalTransformation()
        if copy:
            return self._transformation.copy()
        return self._transformation

    def setTransformation(self, transformation: Matrix):
        self._transformation = transformation.copy() # Make a copy to ensure we never change the given transformation
        self._transformChanged()

    def getOrientation(self) -> Quaternion:
        """Get the local orientation value."""

        return deepcopy(self._orientation)

    def getWorldOrientation(self) -> Quaternion:
        return deepcopy(self._derived_orientation)

    def rotate(self, rotation: Quaternion, transform_space: int = TransformSpace.Local) -> None:
        """Rotate the scene object (and thus its children) by given amount

        :param rotation: :type{Quaternion} A quaternion indicating the amount of rotation.
        :param transform_space: The space relative to which to rotate. Can be any one of the constants in SceneNode::TransformSpace.
        """

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

    def setOrientation(self, orientation: Quaternion, transform_space: int = TransformSpace.Local) -> None:
        """Set the local orientation of this scene node.

        :param orientation: :type{Quaternion} The new orientation of this scene node.
        :param transform_space: The space relative to which to rotate. Can be Local or World from SceneNode::TransformSpace.
        """

        if not self._enabled or orientation == self._orientation:
            return

        if transform_space == SceneNode.TransformSpace.World:
            if self.getWorldOrientation() == orientation:
                return
            new_orientation = orientation * (self.getWorldOrientation() * self._orientation.getInverse()).invert()
            orientation_matrix = new_orientation.toMatrix()
        else:  # Local
            orientation_matrix = orientation.toMatrix()

        euler_angles = orientation_matrix.getEuler()
        new_transform_matrix = Matrix()
        new_transform_matrix.compose(scale = self._scale, angles = euler_angles, translate = self._position, shear = self._shear)
        self._transformation = new_transform_matrix
        self._transformChanged()

    def getScale(self) -> Vector:
        """Get the local scaling value."""

        return self._scale

    def getWorldScale(self) -> Vector:
        return self._derived_scale

    def scale(self, scale: Vector, transform_space: int = TransformSpace.Local) -> None:
        """Scale the scene object (and thus its children) by given amount

        :param scale: :type{Vector} A Vector with three scale values
        :param transform_space: The space relative to which to scale. Can be any one of the constants in SceneNode::TransformSpace.
        """

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

    def setScale(self, scale: Vector, transform_space: int = TransformSpace.Local) -> None:
        """Set the local scale value.

        :param scale: :type{Vector} The new scale value of the scene node.
        :param transform_space: The space relative to which to rotate. Can be Local or World from SceneNode::TransformSpace.
        """

        if not self._enabled or scale == self._scale:
            return
        if transform_space == SceneNode.TransformSpace.Local:
            self.scale(scale / self._scale, SceneNode.TransformSpace.Local)
            return
        if transform_space == SceneNode.TransformSpace.World:
            if self.getWorldScale() == scale:
                return

            self.scale(scale / self._scale, SceneNode.TransformSpace.World)

    def getPosition(self) -> Vector:
        """Get the local position."""

        return self._position

    def getWorldPosition(self) -> Vector:
        """Get the position of this scene node relative to the world."""

        return self._derived_position

    def translate(self, translation: Vector, transform_space: int = TransformSpace.Local) -> None:
        """Translate the scene object (and thus its children) by given amount.

        :param translation: :type{Vector} The amount to translate by.
        :param transform_space: The space relative to which to translate. Can be any one of the constants in SceneNode::TransformSpace.
        """

        if not self._enabled:
            return
        translation_matrix = Matrix()
        translation_matrix.setByTranslation(translation)
        if transform_space == SceneNode.TransformSpace.Local:
            self._transformation.multiply(translation_matrix)
        elif transform_space == SceneNode.TransformSpace.Parent:
            self._transformation.preMultiply(translation_matrix)
        elif transform_space == SceneNode.TransformSpace.World:
            world_transformation = self._world_transformation.copy()
            self._transformation.multiply(self._world_transformation.getInverse())
            self._transformation.multiply(translation_matrix)
            self._transformation.multiply(world_transformation)
        self._transformChanged()

    def setPosition(self, position: Vector, transform_space: int = TransformSpace.Local) -> None:
        """Set the local position value.

        :param position: The new position value of the SceneNode.
        :param transform_space: The space relative to which to rotate. Can be Local or World from SceneNode::TransformSpace.
        """

        if not self._enabled or position == self._position:
            return
        if transform_space == SceneNode.TransformSpace.Local:
            self.translate(position - self._position, SceneNode.TransformSpace.Parent)
        if transform_space == SceneNode.TransformSpace.World:
            if self.getWorldPosition() == position:
                return
            self.translate(position - self._derived_position, SceneNode.TransformSpace.World)

    transformationChanged = Signal()
    """Signal. Emitted whenever the transformation of this object or any child object changes.
    :param object: The object that caused the change.
    """

    def lookAt(self, target: Vector, up: Vector = Vector.Unit_Y) -> None:
        """Rotate this scene node in such a way that it is looking at target.

        :param target: :type{Vector} The target to look at.
        :param up: :type{Vector} The vector to consider up. Defaults to Vector.Unit_Y, i.e. (0, 1, 0).
        """

        if not self._enabled:
            return

        eye = self.getWorldPosition()
        f = (target - eye).normalized()
        up = up.normalized()
        s = f.cross(up).normalized()
        u = s.cross(f).normalized()

        m = Matrix([
            [ s.x,  u.x,  -f.x, 0.0],
            [ s.y,  u.y,  -f.y, 0.0],
            [ s.z,  u.z,  -f.z, 0.0],
            [ 0.0,  0.0,  0.0,  1.0]
        ])

        self.setOrientation(Quaternion.fromMatrix(m))

    def render(self, renderer) -> bool:
        """Can be overridden by child nodes if they need to perform special rendering.
        If you need to handle rendering in a special way, for example for tool handles,
        you can override this method and render the node. Return True to prevent the
        view from rendering any attached mesh data.

        :param renderer: The renderer object to use for rendering.

        :return: False if the view should render this node, True if we handle our own rendering.
        """

        return False

    def isEnabled(self) -> bool:
        """Get whether this SceneNode is enabled, that is, it can be modified in any way."""

        if self._parent is not None and self._enabled:
            return self._parent.isEnabled()
        else:
            return self._enabled

    def setEnabled(self, enable: bool) -> None:
        """Set whether this SceneNode is enabled.

        :param enable: True if this object should be enabled, False if not.
        :sa isEnabled
        """

        self._enabled = enable

    def isSelectable(self) -> bool:
        """Get whether this SceneNode can be selected.

        :note This will return false if isEnabled() returns false.
        """

        return self._enabled and self._selectable

    def setSelectable(self, select: bool) -> None:
        """Set whether this SceneNode can be selected.

        :param select: True if this SceneNode should be selectable, False if not.
        """

        self._selectable = select

    def getBoundingBox(self) -> Optional[AxisAlignedBox]:
        """Get the bounding box of this node and its children."""

        if not self._calculate_aabb:
            return None
        if self._aabb is None:
            self._calculateAABB()
        return self._aabb

    def setCalculateBoundingBox(self, calculate: bool) -> None:
        """Set whether or not to calculate the bounding box for this node.

        :param calculate: True if the bounding box should be calculated, False if not.
        """

        self._calculate_aabb = calculate

    boundingBoxChanged = Signal()

    def getShear(self) -> Vector:
        return self._shear

    def getSetting(self, key: str, default_value: str = "") -> str:
        return self._settings.get(key, default_value)

    def setSetting(self, key: str, value: str) -> None:
        self._settings[key] = value

    def invertNormals(self) -> None:
        for child in self._children:
            child.invertNormals()
        if self._mesh_data:
            self._mesh_data.invertNormals()

    def _transformChanged(self) -> None:
        self._updateTransformation()
        self._resetAABB()
        self.transformationChanged.emit(self)

        for child in self._children:
            child._transformChanged()

    def _updateLocalTransformation(self) -> None:
        self._position, euler_angle_matrix, self._scale, self._shear = self._transformation.decompose()

        self._orientation.setByMatrix(euler_angle_matrix)

    def _updateWorldTransformation(self) -> None:
        if self._parent:
            self._world_transformation = self._parent.getWorldTransformation().multiply(self._transformation)
        else:
            self._world_transformation = self._transformation

        self._derived_position, world_euler_angle_matrix, self._derived_scale, world_shear = self._world_transformation.decompose()
        self._derived_orientation.setByMatrix(world_euler_angle_matrix)

    def _updateTransformation(self) -> None:
        self._updateLocalTransformation()
        self._updateWorldTransformation()
        self._updateCachedNormalMatrix()

    def _resetAABB(self) -> None:
        if not self._calculate_aabb:
            return
        self._aabb = None
        self._bounding_box_mesh = None
        if self._parent:
            self._parent._resetAABB()
        self.boundingBoxChanged.emit()

    def _calculateAABB(self) -> None:
        if self._mesh_data:
            aabb = self._mesh_data.getExtents(self.getWorldTransformation(copy = False))
        else:  # If there is no mesh_data, use a boundingbox that encompasses the local (0,0,0)
            position = self.getWorldPosition()
            aabb = AxisAlignedBox(minimum = position, maximum = position)

        for child in self._children:
            if aabb is None:
                aabb = child.getBoundingBox()
            else:
                aabb = aabb + child.getBoundingBox()
        self._aabb = aabb

    def __str__(self) -> str:
        """String output for debugging."""

        name = self._name if self._name != "" else hex(id(self))
        return "<" + self.__class__.__qualname__ + " object: '" + name + "'>"