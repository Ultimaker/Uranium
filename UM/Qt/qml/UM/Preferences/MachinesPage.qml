// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1

import UM 1.1 as UM

ManagementPage {
    id: base;

    title: catalog.i18nc("@title:tab", "Printers");

    model: UM.MachineInstancesModel
    {
        onRowsInserted: removeEnabled = model.rowCount() > 1
        onRowsRemoved: removeEnabled = model.rowCount() > 1
    }

    onAddObject: model.requestAddMachine();
    onRemoveObject: confirmDialog.open();
    onRenameObject: renameDialog.open();

    removeEnabled: model.rowCount() > 1

    Flow {
        anchors.fill: parent;
        spacing: UM.Theme.sizes.default_margin.height;

        Label { text: base.currentItem && base.currentItem.name ? base.currentItem.name : ""; font: UM.Theme.fonts.large; width: parent.width; }

        Label { text: catalog.i18nc("@label", "Type"); width: parent.width * 0.2; }
        Label { text: base.currentItem && base.currentItem.typeName ? base.currentItem.typeName : ""; width: parent.width * 0.7; }

        UM.I18nCatalog { id: catalog; name: "uranium"; }

        ConfirmRemoveDialog {
            id: confirmDialog;
            object: base.currentItem && base.currentItem.name ? base.currentItem.name : "";
            onYes: base.model.removeMachineInstance(base.currentItem.name);
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
