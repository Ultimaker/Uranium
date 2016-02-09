// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.1


import UM 1.1 as UM

ManagementPage
{
    id: base
    property alias label_printer_name_text: label_printer_name.text
    property alias label_printer_type_text: label_printer_type.text

    title: catalog.i18nc("@title:tab", "Printers")

    model: UM.MachineInstancesModel
    {
        onRowsInserted: removeEnabled = model.rowCount() > 1
        onRowsRemoved: removeEnabled = model.rowCount() > 1
    }

    onAddObject: model.requestAddMachine()
    onRemoveObject: confirmDialog.open()
    onRenameObject: renameDialog.open()

    removeEnabled: model.rowCount() > 1

    Flow
    {
        anchors.fill: parent
        spacing: UM.Theme.sizes.default_margin.height

        Label
        {
                text: base.currentItem.name ? base.currentItem.name : ""
                font: UM.Theme.fonts.large
                width: parent.width
                id: label_printer_name
        }

        Label
        {
                text: catalog.i18nc("@label", "Type")
                width: parent.width * 0.2
                id: label_type
        }
        Label
        {
                text: base.currentItem.typeName ? base.currentItem.typeName : ""
                width: parent.width * 0.7
                id: label_printer_type
        }

        UM.I18nCatalog
        {
            id: catalog
            name: "uranium"
        }

        ConfirmRemoveDialog
        {
            id: confirmDialog
            //object: base.currentItem.name ? base.currentItem.name : ""
            object: base.model.getItem( base.model_list.currentIndex ).name
            onYes:
            {
                //base.model.removeMachineInstance(base.currentItem.name)
                base.model.removeMachineInstance( base.model.getItem( base.model_list.currentIndex ).name )
                base.model_list.forceLayout()
                label_printer_type_text = ""
                label_printer_name_text = ""
            }
        }

        RenameDialog
        {
            id: renameDialog
            //object: base.currentItem.name ? base.currentItem.name : ""
            object: base.model.getItem( base.model_list.currentIndex ).name
            onAccepted:
            {
                //base.model.renameMachineInstance(base.currentItem.name, newName)
                base.model.renameMachineInstance( base.model.getItem( base.model_list.currentIndex ).name, newName )
                base.model_list.forceLayout()
                label_printer_name_text = newName
            }
            onTextChanged: validName = (!base.model.checkInstanceNameExists(newName) || base.currentItem.name == newName).name
        }
     }
}
