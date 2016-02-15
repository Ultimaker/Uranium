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

    model: UM.ProfilesModel { addWorkingProfile: true }

    onAddObject: { var selectedProfile = UM.MachineManager.createProfile(); base.selectProfile(selectedProfile); }
    onRemoveObject: confirmDialog.open();
    onRenameObject: { renameDialog.open(); renameDialog.selectText(); }

    removeEnabled: currentItem != null ? !currentItem.readOnly : false;
    renameEnabled: currentItem != null ? !currentItem.readOnly : false;

    scrollviewCaption: catalog.i18nc("@label %1 is printer name","Printer: %1").arg(UM.MachineManager.activeMachineInstance)

    signal selectProfile(string name)
    onSelectProfile: {
        objectList.currentIndex = objectList.model.find("name", name);
    }

    Item {
        visible: base.currentItem != null
        anchors.fill: parent

        Label { id: profileName; text: base.currentItem ? base.currentItem.name : ""; font: UM.Theme.fonts.large; width: parent.width; }

        ScrollView {
            anchors.left: parent.left
            anchors.top: profileName.bottom
            anchors.topMargin: UM.Theme.sizes.default_margin.height
            anchors.right: parent.right
            anchors.bottom: parent.bottom

            Grid {
                id: containerGrid
                columns: 2
                spacing: UM.Theme.sizes.default_margin.width

                Label { text: catalog.i18nc("@label", "Profile type"); width: 155}
                Label { text: base.currentItem == null ? "" :
                              base.currentItem.id == -1 ? catalog.i18nc("@label", "Current settings") :
                              base.currentItem.readOnly ? catalog.i18nc("@label", "Starter profile (protected)") : catalog.i18nc("@label", "Custom profile"); }

                Column {
                    Repeater {
                            model: base.currentItem ? base.currentItem.settings : null
                            Label {
                                text: modelData.name.toString();
                                width: 155
                                elide: Text.ElideMiddle;
                            }
                    }
                }
                Column {
                    Repeater {
                            model: base.currentItem ? base.currentItem.settings : null
                            Label { text: modelData.value.toString(); }
                    }
                }
            }
        }
    }

    buttons: Row {
        Button
        {
            text: catalog.i18nc("@action:button", "Import");
            iconName: "document-import";
            onClicked: importDialog.open();
        }

        Button
        {
            text: catalog.i18nc("@action:button", "Export");
            iconName: "document-export";
            onClicked: exportDialog.open();
        }
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
            onAccepted: base.model.renameProfile(base.currentItem.name, newName.trim());
        }
        MessageDialog
        {
            id: messageDialog
            title: catalog.i18nc("@window:title", "Import Profile");
            standardButtons: StandardButton.Ok
            modality: Qt.ApplicationModal
        }

        FileDialog
        {
            id: importDialog;
            title: catalog.i18nc("@title:window", "Import Profile");
            selectExisting: true;
            nameFilters: base.model.getFileNameFiltersRead()
            folder: base.model.getDefaultSavePath()

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
                    messageDialog.icon = StandardIcon.Critical
                }
                messageDialog.open()
            }
        }

        FileDialog
        {
            id: exportDialog;
            title: catalog.i18nc("@title:window", "Export Profile");
            selectExisting: false;
            nameFilters: base.model.getFileNameFiltersWrite()
            folder: base.model.getDefaultSavePath()
            onAccepted:
            {
                var result =  base.model.exportProfile(base.currentItem.name, fileUrl, selectedNameFilter)
                if(result.status == "error")
                {
                    messageDialog.icon = StandardIcon.Critical
                    messageDialog.text = result.message
                    messageDialog.open()
                }
                // else pop-up Message thing from python code
            }
        }
    }
}
