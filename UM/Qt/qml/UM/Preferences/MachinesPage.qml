// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1

import UM 1.1 as UM

ManagementPage {
    id: base;

    title: catalog.i18nc("@title:tab", "Printers");
    property int numInstances: model.count
    model: UM.MachineInstancesModel
    {
        onDataChanged: numInstances = model.count
    }

    onAddObject: model.requestAddMachine();
    onRemoveObject: confirmDialog.open();
    onRenameObject: renameDialog.open();
    onActivateObject: if (activateEnabled) { UM.MachineManager.setActiveMachineInstance(currentItem.name) }

    activateEnabled: currentItem != null && !currentItem.active
    removeEnabled: numInstances > 1
    renameEnabled: numInstances > 0

    Flow {
        anchors.fill: parent;
        spacing: UM.Theme.getSize("default_margin").height;

        Label {
            text: base.currentItem && base.currentItem.name ? base.currentItem.name : ""
            font: UM.Theme.getFont("large_bold")
            width: parent.width
            elide: Text.ElideRight
        }

        Label {
            text: catalog.i18nc("@label", "Type");
            width: Math.round(parent.width * 0.2);
        }

        Label {
            text: base.currentItem && base.currentItem.typeName ? base.currentItem.typeName : "";
            width: Math.round(parent.width * 0.7);
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }

        ConfirmRemoveDialog {
            id: confirmDialog;
            object: base.currentItem && base.currentItem.name ? base.currentItem.name : "";
            onYes: {
                base.model.removeMachineInstance(base.currentItem.name);
                base.objectList.currentIndex = base.activeIndex();
            }
        }
        RenameDialog {
            id: renameDialog;
            object: base.currentItem && base.currentItem.name ? base.currentItem.name : "";
            onAccepted: {
                base.model.renameMachineInstance(base.currentItem.name, newName.trim());
                //Reselect current item to update details panel
                var index = objectList.currentIndex
                objectList.currentIndex = -1
                objectList.currentIndex = index
            }
        }
    }
}
