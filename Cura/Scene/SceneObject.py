from Cura import Trans

class SceneObject(object):
    def __init__(self):
        self._children = []
        self._mesh_data = None
        self._transformation = None #Transformation of this SceneObject with respect to its parent (or origin in case of root)
        bla = Transformations.identity_matrix()
        
    def getMeshData(self):
        return self._mesh_data
    
    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data
    
    def addChild(self, scene_object):
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
    
    # Computes and returns the transformation with respect to origin
    def getGlobalTransformation(self):
        ##TODO: Implement finding the global transformation with respect to origin
        pass 
    
    # Returns the local transofmration with respect to its parent.
    # \retuns transformation 4x4 (homogenous) matrix
    def getLocalTransformation(self):
        return self._transformation
    
    # Sets the local transofmration with respect to its parent.
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