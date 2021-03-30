// Copyright (c) 2019 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.1

import UM 1.1 as UM

UM.Dialog
{
    id: base
    property string object: ""

    property alias newName: nameField.text
    property bool validName: true
    property string validationError
    property string dialogTitle: catalog.i18nc("@title:window", "Rename")
    property string explanation: catalog.i18nc("@info", "Please provide a new name.")

    title: dialogTitle

    minimumWidth: UM.Theme.getSize("small_popup_dialog").width
    minimumHeight: UM.Theme.getSize("small_popup_dialog").height
    width: minimumWidth
    height: minimumHeight

    property variant catalog: UM.I18nCatalog { name: "uranium" }

    signal textChanged(string text)
    signal selectText()
    onSelectText:
    {
        nameField.selectAll();
        nameField.focus = true;
    }

    Column
    {
        anchors.fill: parent

        Label
        {
            text: base.explanation + "\n" //Newline to make some space using system theming.
            width: parent.width
            wrapMode: Text.WordWrap
        }

        TextField
        {
            id: nameField
            width: parent.width
            text: base.object
            maximumLength: 40
            onTextChanged: base.textChanged(text)
        }

        Label
        {
            visible: !base.validName
            text: base.validationError
        }
    }

    rightButtons: [
        Button
        {
            id: cancelButton
            text: catalog.i18nc("@action:button","Cancel")
            onClicked: base.reject()
        },
        Button
        {
            text: catalog.i18nc("@action:button", "OK")
            onClicked: base.accept()
            enabled: base.validName
            isDefault: true
        }
    ]
}

