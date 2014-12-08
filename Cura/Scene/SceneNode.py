from Cura.Math.Matrix import Matrix
from Cura.Math.Vector import Vector
from Cura.Signal import Signal, SignalEmitter
from copy import copy, deepcopy

import math

##  A scene node object.
#
#   These objects can hold a mesh and multiple children. Each node has a transformation matrix
#   that maps it it's parents space to the local space (it's inverse maps local space to parent).
#
#   \todo Add unit testing
class SceneNode(SignalEmitter):
    def __init__(self, parent = None):
        super().__init__() # Call super to make multiple inheritence work.

        self._children = []
        self._mesh_data = None
        self._transformation = Matrix()
        self._parent = parent
        self._locked = False
        if parent:
            parent.addChild(self)

    ##  Get the parent of this node. If the node has no parent, it is the root node.
    #   \returns SceneNode if it has a parent and None if it's the root node.
    def getParent(self):
        return self._parent

    ##  Set the parent of this object
    #   \param scene_node SceneNode that is the parent of this object.
    def setParent(self, scene_node):
        self._parent = scene_node
        self.parentChanged.emit()

    ##  Emitted whenever the parent changes.
    parentChanged = Signal()

    ##  Get the (original) mesh data from the scene node/object. 
    #   \returns MeshData
    def getMeshData(self):
        return self._mesh_data

    ##  Get the transformed mesh data from the scene node/object, based on the transformation of scene nodes wrt root. 
    #   \returns MeshData    
    def getMeshDataTransformed(self):
        transformed_mesh = deepcopy(self._mesh_data)
        transformed_mesh.transform(self.getGlobalTransformation())
        return transformed_mesh

    ##  Set the mesh of this node/object
    #   \param mesh_data MeshData object
    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data
        self.meshDataChanged.emit(self)

    ##  Emitted whenever the attached mesh data object changes.
    meshDataChanged = Signal()

    ##  Add a child to this node and set it's parent as this node.
    #   \params scene_node SceneNode to add.
    def addChild(self, scene_node):
        scene_node.setParent(self)
        scene_node.transformationChanged.connect(self.transformationChanged)
        scene_node.childrenChanged.connect(self.childrenChanged)
        self._children.append(scene_node)
        self.childrenChanged.emit(self)

    def removeChild(self):
        # TODO : We need to think about how children are removed (if ever?).
        self.childrenChanged.emit(self)
        pass

    ##  Removes all children and its children's children.
    def removeAllChildren(self):
        for child in self._children:
            child.removeAllChildren()
        del self._children[:] #Actually destroy the children (and not just replace it with empty list
        self.childrenChanged.emit(self)

    ##  Get the list of direct children
    #   \returns List of children
    def getChildren(self):
        return self._children

    ##  Get list of all children (including it's children children children etc.)
    #   \returns list ALl children in this 'tree'
    def getAllChildren(self):
        children = []
        children.extend(self._children)
        for child in self._children:
            children.extend(child.getAllChildren())
        return children

    ##  Emitted whenever the list of children of this object or any child object changes.
    #   \param object The object that triggered the change.
    childrenChanged = Signal()

    ##  Computes and returns the transformation from origin to local space
    #   \returns 4x4 transformation matrix
    def getGlobalTransformation(self):
        if(self._parent is None):
            return self._transformation
        else:
            global_transformation = deepcopy(self._transformation)
            global_transformation.preMultiply(self._parent.getGlobalTransformation())
            return global_transformation

    ##  Returns the local transformation with respect to its parent. (from parent to local)
    #   \retuns transformation 4x4 (homogenous) matrix
    def getLocalTransformation(self):
        return self._transformation

    ##  Sets the local transformation with respect to its parent. (from parent to local)
    #   \param transformation 4x4 (homogenous) matrix
    def setLocalTransformation(self, transformation):
        if self._locked:
            return

        self._transformation = transformation
        self.transformationChanged.emit(self)

    ##  Rotate the scene object (and thus its children) by given amount
    def rotate(self, rotation):
        if self._locked:
            return

        rotMatrix = Matrix()
        rotMatrix.setByQuaternion(rotation)
        self._transformation.multiply(rotMatrix)
        self.transformationChanged.emit(self)

    def rotateByAngleAxis(self, angle, axis):
        if self._locked:
            return

        self._transformation.rotateByAxis(math.radians(angle), axis)
        self.transformationChanged.emit(self)

    ##  Scale the scene object (and thus its children) by given amount
    def scale(self, scale):
        self._transformation.scaleByFactor(scale)
        self.transformationChanged.emit(self)
        pass

    ##  Translate the scene object (and thus its children) by given amount.
    #   \param translation Vector(x,y,z).
    def translate(self, translation):
        if self._locked:
            return

        self._transformation.translate(translation)
        self.transformationChanged.emit(self)

    ##  Set
    def setPosition(self, position):
        if self._locked:
            return

        self._transformation.setByTranslation(position)
        self.transformationChanged.emit(self)

    def getPosition(self):
        pos = self._transformation.getData()
        return Vector(pos[0,3], pos[1,3], pos[2,3])

    def getGlobalPosition(self):
        pos = self.getGlobalTransformation().getData()
        return Vector(float(pos[0,3]), pos[1,3], pos[2,3])

    ##  Signal. Emitted whenever the transformation of this object or any child object changes.
    #   \param object The object that caused the change.
    transformationChanged = Signal()
    
    ##  Check if this node is at the bottom of the tree (and thus a leaf node).
    #   \returns True if its a leaf object, false otherwise.
    def isLeafNode(self):
        if len(self._children) == 0:
            return True
        return False

    ##  Can be overridden by child nodes if they need to perform special rendering.
    #   If you need to handle rendering in a special way, for example for tool handles,
    #   you can override this method and render the node. Return True to prevent the
    #   view from rendering any attached mesh data.
    #
    #   \return False if the view should render this node, True if we handle our own rendering.
    def render(self):
        return False

    ##  Get whether this SceneNode is locked, that is, its transformation relative to its parent should not change.
    def isLocked(self):
        return self._locked

    ##  Set whether this SceneNode is locked.
    #   \param lock True if this object should be locked, False if not.
    #   \sa isLocked
    def setLocked(self, lock):
        self._locked = lock


