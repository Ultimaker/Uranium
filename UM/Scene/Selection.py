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

    __selection = []
