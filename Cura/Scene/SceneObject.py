from Cura.Math.Matrix import Matrix
from Cura.Signal import Signal
from copy import copy, deepcopy

## \brief A scene node object. These objects can hold a mesh and multiple children. Each node has a transformation matrix
#         that maps it it's parents space to the local space (it's inverse maps local space to parent).
#
#   \todo Add unit testing
class SceneObject(object):
    def __init__(self, parent = None):
        # Signals
        self.parentChanged = Signal()
        self.childrenChanged = Signal()
        self.transformationChanged = Signal()

        self._children = []
        self._mesh_data = None
        self._transformation = Matrix()
        self._parent = parent
        if parent:
            parent.addChild(self)

    ## Get the parent of this node. If the node has no parent, it is the root node.
    # \returns SceneObject if it has a parent and None if it's the root node.
    def getParent(self):
        return self._parent
    
    ## Set the parent of this object
    # \param scene_object SceneObject that is the parent of this object.
    def setParent(self, scene_object):
        self._parent = scene_object
        self.parentChanged.emit()

    ##  Signal. Emitted whenever the parent changes.
    parentChanged = None
    
    ## Get the (original) mesh data from the scene node/object. 
    # \returns MeshData
    def getMeshData(self):
        return self._mesh_data
    
    ## Get the transformed mesh data from the scene node/object, based on the transformation of scene nodes wrt root. 
    # \returns MeshData    
    def getMeshDataTransformed(self):
        transformed_mesh = deepcopy(self._mesh_data)
        transformed_mesh.transform(self.getGlobalTransformation())
        return transformed_mesh
    
    ## Set the mesh of this node/object
    # \param mesh_data MeshData object
    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data
        self.meshDataChanged.emit(self)

    ##  Signal. Emitted whenever the attached mesh data object changes.
    meshDataChanged = Signal()
    
    ## Add a child to this node and set it's parent as this node.
    # \params scene_object SceneObject to add.
    def addChild(self, scene_object):
        scene_object.setParent(self)
        scene_object.transformationChanged.connect(self.transformationChanged)
        scene_object.childrenChanged.connect(self.childrenChanged)
        self._children.append(scene_object)
        self.childrenChanged.emit(self)
        
    def removeChild(self):
        # TODO : We need to think about how children are removed (if ever?).
        self.childrenChanged.emit(self)
        pass
    
    ## Removes all children and its children's children.
    def removeAllChildren(self):
        for child in self._children:
            child.removeAllChildren()
        del self._children[:] #Actually destroy the children (and not just replace it with empty list
        self.childrenChanged.emit(self)
    
    ## Get the list of direct children
    # \returns List of children
    def getChildren(self):
        return self._children
    
    ## Get list of all children (including it's children children children etc.)
    # \returns list ALl children in this 'tree'
    def getAllChildren(self):
        children = []
        for child in self._children:
            children.extend(child.getAllChildren())

    ##  Signal. Emitted whenever the list of children of this object or any child object changes.
    #   \param object The object that triggered the change.
    childrenChanged = None
    
    ## Computes and returns the transformation from origin to local space
    # \returns 4x4 transformation matrix
    def getGlobalTransformation(self):
        if(self._parent is None):
            return self._transformation
        else:
            global_transformation = deepcopy(self._transformation)
            global_transformation.preMultiply(self._parent.getGlobalTransformation())
            return global_transformation
    
    ## Returns the local transformation with respect to its parent. (from parent to local)
    # \retuns transformation 4x4 (homogenous) matrix
    def getLocalTransformation(self):
        return self._transformation
    
    ## Sets the local transformation with respect to its parent. (from parent to local)
    # \param transformation 4x4 (homogenous) matrix
    def setLocalTransformation(self, transformation):
        self._transformation = transformation
        self.transformationChanged.emit(self)
    
    ## Rotate the scene object (and thus its children) by given amount
    def rotate(self, rotation):
        rotMatrix = Matrix()
        rotMatrix.setByQuaternion(rotation)
        self._transformation.multiply(rotMatrix)
        self.transformationChanged.emit(self)

    def rotateByAngleAxis(self, angle, axis):
        self._transformation.rotateByAxis(angle, axis)
        self.transformationChanged.emit(self)
    
    ## Scale the scene object (and thus its children) by given amount
    def scale(self, scale):
        #TODO Implement
        self.transformationChanged.emit(self)
        pass
    
    ## Translate the scene object (and thus its children) by given amount.
    # \param translation Vector(x,y,z).
    def translate(self, translation):
        self._transformation.translate(translation)
        self.transformationChanged.emit(self)

    ## Set
    def setPosition(self, position):
        self._transformation.setByTranslation(position)
        self.transformationChanged.emit(self)

    ##  Signal. Emitted whenever the transformation of this object or any child object changes.
    #   \param object The object that caused the change.
    transformationChanged = None
    
    ## Check if this node is at the bottom of the tree (and thus a leaf node).
    # \returns True if its a leaf object, false otherwise.
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

