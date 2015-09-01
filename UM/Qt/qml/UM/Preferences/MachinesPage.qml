// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1

import UM 1.1 as UM

ManagementPage {
    id: base;

    title: catalog.i18nc("@title", "Machines");

    model: UM.MachineInstancesModel { }

    onAddObject: model.requestAddMachine();
    onRemoveObject: confirmDialog.open();
    onRenameObject: renameDialog.open();

    removeEnabled: model.rowCount() > 1;

    Flow {
        anchors.fill: parent;
        spacing: UM.Theme.sizes.default_margin.height;

        Label { text: base.currentItem.name; font: UM.Theme.fonts.large; width: parent.width; }

        Label { text: catalog.i18nc("@label", "Type"); width: parent.width * 0.2; }
        Label { text: base.currentItem.typeName; width: parent.width * 0.7; }

        Label { visible: base.currentItem.hasVariants; text: catalog.i18nc("@label", "Variant"); width: parent.width * 0.2; }
        Label { visible: base.currentItem.hasVariants; text: base.currentItem.variantName; width: parent.width * 0.7; }

        UM.I18nCatalog { id: catalog; name: "uranium"; }

        ConfirmRemoveDialog {
            id: confirmDialog;
            object: base.currentItem.name;
            onYes: base.model.removeMachineInstance(base.currentItem.name);
        }
        RenameDialog {
            id: renameDialog;
            object: base.currentItem.name;
            onAccepted: base.model.renameMachineInstance(base.currentItem.name, newName);
        }
    }
}
