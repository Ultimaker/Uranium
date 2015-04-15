from UM.Signal import Signal

class Selection:
    @classmethod
    def add(cls, object):
        if not object in cls.__selection:
            cls.__selection.append(object)
            cls.selectionChanged.emit()

    @classmethod
    def remove(cls, object):
        if object in cls.__selection:
            cls.__selection.remove(object)
            cls.selectionChanged.emit()

    @classmethod
    def getCount(cls):
        return len(cls.__selection)

    @classmethod
    def getAllSelectedObjects(cls):
        return cls.__selection

    @classmethod
    def getSelectedObject(cls, index):
        return cls.__selection[index]

    @classmethod
    def isSelected(cls, object):
        return object in cls.__selection

    @classmethod
    def clear(cls):
        cls.__selection.clear()
        cls.selectionChanged.emit()

    @classmethod
    def hasSelection(cls):
        return bool(cls.__selection)

    selectionChanged = Signal()

    @classmethod
    def getAveragePosition(cls):
        if not cls.__selection:
            return Vector(0, 0, 0)

        if len(cls.__selection) == 1:
            node = cls.__selection[0]
            if node.getBoundingBox() and node.getBoundingBox().isValid():
                return node.getBoundingBox().center
            else:
                return node.getWorldPosition()

        pos = Vector()
        for node in cls.__selection:
            if node.getBoundingBox() and node.getBoundingBox().isValid():
                pos += node.getBoundingBox().center
            else:
                pos += node.getWorldPosition()

        pos /= len(cls.__selection)

        return pos

    __selection = []
