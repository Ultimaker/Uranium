# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List, Optional, Tuple

from UM.Signal import Signal
from UM.Math.Vector import Vector
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Scene.SceneNode import SceneNode

from UM.Operations.GroupedOperation import GroupedOperation


class Selection:
    """This class is responsible for keeping track of what objects are selected

    It uses signals to notify others of changes in the selection
    It also has a convenience function that allows it to apply a single operation
    to all selected objects.
    """

    @classmethod
    def add(cls, object: SceneNode) -> None:
        if object not in cls.__selection:
            cls.__selection.append(object)
            object.transformationChanged.connect(cls._onTransformationChanged)
            cls._onTransformationChanged(object)
            cls.selectionChanged.emit()

    @classmethod
    def remove(cls, object: SceneNode) -> None:
        if object in cls.__selection:
            cls.__selection.remove(object)
            cls.unsetFace(object)
            object.transformationChanged.disconnect(cls._onTransformationChanged)
            cls._onTransformationChanged(object)
            cls.selectionChanged.emit()

    @classmethod
    def getFaceSelectMode(cls) -> bool:
        return cls.__face_select_mode

    @classmethod
    def setFaceSelectMode(cls, select: bool) -> None:
        if select != cls.__face_select_mode:
            cls.__face_select_mode = select
            cls.selectedFaceChanged.emit()

    @classmethod
    def setFace(cls, object: SceneNode, face_id: int) -> None:
        # Don't force-add the object, as the parent may be the 'actual' selected one.
        cls.__selected_face = (object, face_id)
        cls.selectedFaceChanged.emit()

    @classmethod
    def unsetFace(cls, object: Optional["SceneNode"] = None) -> None:
        if object is None or cls.__selected_face is None or object == cls.__selected_face[0]:
            cls.__selected_face = None
            cls.selectedFaceChanged.emit()

    @classmethod
    def toggleFace(cls, object: SceneNode, face_id: int) -> None:
        current_face = cls.__selected_face
        if current_face is None or object != current_face[0] or face_id != current_face[1]:
            cls.setFace(object, face_id)
        else:
            cls.unsetFace(object)

    @classmethod
    def hoverFace(cls, object: SceneNode, face_id: int) -> None:
        current_hover = cls.__hover_face
        if current_hover is None or object != current_hover[0] or face_id != current_hover[1]:
            # Don't force-add the object, as the parent may be the 'actual' selected one.
            cls.__hover_face = (object, face_id)
            cls.hoverFaceChanged.emit()

    @classmethod
    def unhoverFace(cls, object: Optional["SceneNode"] = None) -> None:
        if object is None or not cls.__hover_face or object == cls.__hover_face[0]:
            cls.__hover_face = None
            cls.hoverFaceChanged.emit()

    @classmethod
    def getCount(cls) -> int:
        """Get number of selected objects"""

        return len(cls.__selection)

    @classmethod
    def getAllSelectedObjects(cls) -> List[SceneNode]:
        return cls.__selection

    @classmethod
    def getSelectedFace(cls) -> Optional[Tuple[SceneNode, int]]:
        return cls.__selected_face

    @classmethod
    def getHoverFace(cls) -> Optional[Tuple[SceneNode, int]]:
        return cls.__hover_face

    @classmethod
    def getBoundingBox(cls) -> AxisAlignedBox:
        bounding_box = None  # don't start with an empty bounding box, because that includes (0,0,0)
        for node in cls.__selection:
            if not bounding_box:
                bounding_box = node.getBoundingBox()
            else:
                bounding_box = bounding_box + node.getBoundingBox()

        if not bounding_box:
            bounding_box = AxisAlignedBox.Null

        return bounding_box

    @classmethod
    def getSelectedObject(cls, index: int) -> Optional[SceneNode]:
        """Get selected object by index

        :param index: index of the object to return
        :returns: selected object or None if index was incorrect / not found
        """

        try:
            return cls.__selection[index]
        except IndexError:
            return None

    @classmethod
    def isSelected(cls, object: SceneNode) -> bool:
        return object in cls.__selection

    @classmethod
    def clear(cls) -> None:
        cls.__selection.clear()
        cls.selectionChanged.emit()

    @classmethod
    def clearFace(cls) -> None:
        cls.__selected_face = None
        cls.__hover_face = None
        cls.selectedFaceChanged.emit()
        cls.hoverFaceChanged.emit()

    @classmethod
    def hasSelection(cls) -> bool:
        """Check if anything is selected at all."""

        return bool(cls.__selection)

    selectionChanged = Signal()

    selectionCenterChanged = Signal()

    selectedFaceChanged = Signal()

    hoverFaceChanged = Signal()

    @classmethod
    def getSelectionCenter(cls) -> Vector:
        if cls.__selection_center is None:
            cls.__selection_center = cls.getBoundingBox().center
        return cls.__selection_center

    @classmethod
    def applyOperation(cls, operation, *args, **kwargs):
        """Apply an operation to the entire selection

        This will create and push an operation onto the operation stack. Dependent
        on whether there is one item selected or multiple it will be just the
        operation or a grouped operation containing the operation for each selected
        node.

        :param operation: :type{Class} The operation to create and push. It should take a SceneNode as first positional parameter.
        :param args: The additional positional arguments passed along to the operation constructor.
        :param kwargs: The additional keyword arguments that will be passed along to the operation constructor.

        :return: list of instantiated operations
        """

        if not cls.__selection:
            return

        operations = []

        if len(cls.__selection) == 1:
            node = cls.__selection[0]
            op = operation(node, *args, **kwargs)
            operations.append(op)
        else:
            op = GroupedOperation()

            for node in Selection.getAllSelectedObjects():
                sub_op = operation(node, *args, **kwargs)
                op.addOperation(sub_op)
                operations.append(sub_op)

        op.push()
        return operations

    @classmethod
    def _onTransformationChanged(cls, _) -> None:
        cls.__selection_center = None
        cls.selectionCenterChanged.emit()

    __selection = []    # type: List[SceneNode]
    __selection_center = None  # type: Optional[Vector]
    __selected_face = None    # type: Optional[Tuple[SceneNode, int]]
    __hover_face = None    # type: Optional[Tuple[SceneNode, int]]
    __face_select_mode = False
