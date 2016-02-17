// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.1

import UM 1.1 as UM

UM.Dialog
{
    id: base;
    property string object: "";

    property alias newName: nameField.text;
    property bool validName: true;
    property string validationError;

    title: catalog.i18nc("@title:window", "Name Copy");

    minimumWidth: 400 * Screen.devicePixelRatio;
    minimumHeight: 120 * Screen.devicePixelRatio;
    width: minimumWidth
    height: minimumHeight

    property variant catalog: UM.I18nCatalog { name: "uranium"; }

    signal textChanged(string text);
    signal selectText()
    onSelectText: {
        nameField.selectAll();
        nameField.focus = true;
    }

    Column {
        anchors.fill: parent;

        TextField {
            id: nameField;
            width: parent.width;
            text: base.object;
            onTextChanged: base.textChanged(text);
        }

        Label {
            visible: !base.validName;
            text: base.validationError;
        }
    }

    rightButtons: [
        Button {
            text: catalog.i18nc("@action:button","Cancel");
            onClicked: base.reject();
        },
        Button {
            text: catalog.i18nc("@action:button", "Ok");
            onClicked: base.accept();
            enabled: base.validName;
            isDefault: true;
        }

    ]
}

