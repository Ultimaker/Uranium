// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2

import UM 1.1 as UM

ManagementPage
{
    id: base;

    title: catalog.i18nc("@title:tab", "Profiles");

    detailsVisible: false;

    model: UM.ProfilesModel { }

    onAddObject: importDialog.open();
    onRemoveObject: confirmDialog.open();
    onRenameObject: renameDialog.open();

    addText: catalog.i18nc("@action:button", "Import");

    removeEnabled: currentItem != null ? !currentItem.readOnly : false;
    renameEnabled: currentItem != null ? !currentItem.readOnly : false;

    buttons: Button
    {
        text: catalog.i18nc("@action:button", "Export");
        iconName: "document-export";
        onClicked: exportDialog.open();
    }

    Item
    {
        UM.I18nCatalog { id: catalog; name: "uranium"; }

        ConfirmRemoveDialog
        {
            id: confirmDialog;
            object: base.currentItem != null ? base.currentItem.name : "";
            onYes: base.model.removeProfile(base.currentItem.name);
        }
        RenameDialog
        {
            id: renameDialog;
            object: base.currentItem != null ? base.currentItem.name : "";
            onTextChanged: validName = !(base.model.checkProfileExists(text) && object != text);
            onAccepted: base.model.renameProfile(base.currentItem.name, newName);
            validationError: "A profile with that name already exists!";
        }
        MessageDialog
        {
            id: messageDialog
            title: catalog.i18nc("@window:title", "Import Profile");
            standardButtons: StandardButton.Ok
            modality: Qt.ApplicationModel
        }

        FileDialog
        {
            id: importDialog;
            title: catalog.i18nc("@title:window", "Import Profile");
            selectExisting: true;
            nameFilters: [ catalog.i18nc("@item:inlistbox", "Cura Profiles (*.curaprofile)"), catalog.i18nc("@item:inlistbox", "All Files (*)") ]

            onAccepted:
            {
                var result = base.model.importProfile(fileUrl)
                messageDialog.text = result.message
                if(result.status == "ok")
                {
                    messageDialog.icon = StandardIcon.Information
                }
                else if(result.status == "duplicate")
                {
                    messageDialog.icon = StandardIcon.Warning
                }
                else
                {
                    messageDialog.icon = StandardIcon.Error
                }
                messageDialog.open()
            }
        }

        FileDialog
        {
            id: exportDialog;
            title: catalog.i18nc("@title:window", "Export Profile");
            selectExisting: false;
            nameFilters: [ catalog.i18nc("@item:inlistbox", "Cura Profiles (*.curaprofile)") ]

            onAccepted: base.model.exportProfile(base.currentItem.name, fileUrl)
        }
    }
}
