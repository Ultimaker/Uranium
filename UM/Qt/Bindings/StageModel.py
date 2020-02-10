# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from PyQt5.QtCore import Qt

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.Qt.ListModel import ListModel


class StageModel(ListModel):
    """The StageModel is a representation of all stages in QML.

    Use it to populate a stage based menu (like top bar).
    """

    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    StageRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = Application.getInstance().getController()
        self._controller.stagesChanged.connect(self._onStagesChanged)
        self._onStagesChanged()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.StageRole, "stage")

    def _onStagesChanged(self):
        items = []
        stages = self._controller.getAllStages()

        for stage_id, stage in stages.items():
            view_meta_data = PluginRegistry.getInstance().getMetaData(stage_id).get("stage", {})

            # Skip view modes that are marked as not visible
            if "visible" in view_meta_data and not view_meta_data["visible"]:
                continue

            # Metadata elements
            name = view_meta_data.get("name", stage_id)
            weight = view_meta_data.get("weight", 99)

            items.append({
                "id": stage_id,
                "name": name,
                "stage": stage,
                "weight": weight
            })

        items.sort(key=lambda t: t["weight"])
        self.setItems(items)
