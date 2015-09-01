// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2

import UM 1.1 as UM

ManagementPage {
    id: base;

    title: catalog.i18nc("@title", "Profiles");

    detailsVisible: false;

    model: UM.ProfilesModel { }

    onAddObject: importDialog.open();
    onRemoveObject: confirmDialog.open();
    onRenameObject: renameDialog.open();

    addText: catalog.i18nc("@action:button", "Import");

    removeEnabled: currentItem != null ? !currentItem.readOnly : false;
    renameEnabled: currentItem != null ? !currentItem.readOnly : false;

    buttons: Button {
        text: catalog.i18nc("@action:button", "Export");
        iconName: "document-export";
        onClicked: exportDialog.open();
    }

    Item {
        UM.I18nCatalog { id: catalog; name: "uranium"; }

        ConfirmRemoveDialog {
            id: confirmDialog;
            object: base.currentItem.name;
            onYes: base.model.removeProfile(base.currentItem.name);
        }
        RenameDialog {
            id: renameDialog;
            object: base.currentItem.name;
            onAccepted: base.model.renameProfile(base.currentItem.name, newName);
        }

        FileDialog {
            id: importDialog;
            title: catalog.i18nc("@title", "Import Profile");
            selectExisting: true;
            nameFilters: [ catalog.i18nc("@item:inlistbox", "Cura Profiles (*.curaprofile)"), catalog.i18nc("@item:inlistbox", "All Files (*)") ]

            onAccepted: base.model.importProfile(fileUrl)
        }

        FileDialog {
            id: exportDialog;
            title: catalog.i18nc("@title", "Export Profile");
            selectExisting: false;
            nameFilters: [ catalog.i18nc("@item:inlistbox", "Cura Profiles (*.curaprofile)") ]

            onAccepted: base.model.exportProfile(base.currentItem.name, fileUrl)
        }
    }
}
