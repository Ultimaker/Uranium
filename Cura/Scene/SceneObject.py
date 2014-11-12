from Cura.Math.Matrix import Matrix
from copy import copy, deepcopy

class SceneObject(object):
    def __init__(self, parent = None):
        self._children = []
        self._mesh_data = None
        self._transformation = Matrix() #Transformation of this SceneObject with respect to its parent (or origin in case of root)
        self._parent = parent
        #print(self._transformation.getData())
        
    # Get the parent of this node. If the node has no parent, it is the root node.
    def getParent(self):
        return self._parent
    
    def setParent(self, scene_object):
        self._parent = scene_object
    
    # Get the mesh data from the scene node/object. 
    # \param transformed False if you want the original (un-scaled/rotated/transformed) mesh and True if you do want this.
    # \returns mesh_data
    def getMeshData(self,transformed = True):
        if(transformed):
            transformed_mesh = deepcopy(self._mesh_data)
            transformed_mesh.transform(self.getGlobalTransformation())
            return transformed_mesh
        else:
            return self._mesh_data
    
    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data
    
    # Add a child to this node and set it's parent as this node.
    def addChild(self, scene_object):
        scene_object.setParent(self)
        self._children.append(scene_object)
        
        
    def removeChild(self):
        #TODO: We need to think about how children are removed (if ever?).
        pass
    
    # Removes all children and its children's children.
    def removeAllChildren(self):
        for child in self._children:
            child.removeAllChildren()
        del self._children[:] #Actually destroy the children (and not just replace it with empty list
    
    # Returns a list of local children
    def getChildren(self):
        return self._children
    
    # Computes and returns the transformation from origin to local space
    def getGlobalTransformation(self):
        #print("Own transformation" + self._transformation.getData())
        ##TODO: Implement finding the global transformation with respect to origin
        
        if(self._parent is None):
            return self._transformation
        else:
            global_transformation = deepcopy(self._transformation)
            global_transformation.preMultiply(self._parent.getGlobalTransformation())
            return global_transformation
    
    # Returns the local transformation with respect to its parent. (from parent to local)
    # \retuns transformation 4x4 (homogenous) matrix
    def getLocalTransformation(self):
        return self._transformation
    
    # Sets the local transformation with respect to its parent. (from parent to local)
    # \param transformation 4x4 (homogenous) matrix
    def setLocalTransformation(self, transformation):
        self._transformation = transformation
    
    # Rotate the scene object (and thus its children) by given amount
    def rotate(self, rotation):
        pass
    
    # Scale the scene object (and thus its children) by given amount
    def scale(self, scale):
        pass
    
    # Translate the scene object (and thus its children) by given amount
    def translate(self, translation):
        pass
    
    # Check if this node is at the bottom of the tree (and thus a leaf node)
    def isLeafNode(self):
        if len(self._children) == 0:
            return True
        return False