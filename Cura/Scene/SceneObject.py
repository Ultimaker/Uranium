from Cura.Math.Matrix import Matrix
from copy import copy, deepcopy


## \brief A scene node object. These objects can hold a mesh and multiple children. Each node has a transformation matrix
#         that maps it it's parents space to the local space (it's inverse maps local space to parent). 
class SceneObject(object):
    def __init__(self, parent = None):
        self._children = []
        self._mesh_data = None
        self._transformation = Matrix() 
        self._parent = parent
        
    ## Get the parent of this node. If the node has no parent, it is the root node.
    # \returns SceneObject if it has a parent and None if it's the root node.
    def getParent(self):
        return self._parent
    
    ## Set the parent of this object
    # \param scene_object SceneObject that is the parent of this object.
    def setParent(self, scene_object):
        self._parent = scene_object
    
    ## Get the (original) mesh data from the scene node/object. 
    # \returns MeshData
    def getMeshData(self,transformed = True):
        return self._mesh_data
    
    ## Get the transformed mesh data from the scene node/object, based on the transformation of scene nodes wrt root. 
    # \returns MeshData    
    def getMeshDataTransformed):
        transformed_mesh = deepcopy(self._mesh_data)
        transformed_mesh.transform(self.getGlobalTransformation())
        return transformed_mesh
    
    ## Set the mesh of this node/object
    # \param mesh_data MeshData object
    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data
    
    ## Add a child to this node and set it's parent as this node.
    # \params scene_object SceneObject to add.
    def addChild(self, scene_object):
        scene_object.setParent(self)
        self._children.append(scene_object)
        
    def removeChild(self):
        # TODO : We need to think about how children are removed (if ever?).
        pass
    
    ## Removes all children and its children's children.
    def removeAllChildren(self):
        for child in self._children:
            child.removeAllChildren()
        del self._children[:] #Actually destroy the children (and not just replace it with empty list
    
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
    
    ## Rotate the scene object (and thus its children) by given amount
    def rotate(self, rotation):
        #TODO: Implement
        pass
    
    ## Scale the scene object (and thus its children) by given amount
    def scale(self, scale):
        #TODO Implement
        pass
    
    ## Translate the scene object (and thus its children) by given amount.
    # \param translation Vector(x,y,z).
    def translate(self, translation):
        self._transformation.translate(translation)
    
    ## Check if this node is at the bottom of the tree (and thus a leaf node).
    # \returns True if its a leaf object, false otherwise.
    def isLeafNode(self):
        if len(self._children) == 0:
            return True
        return False