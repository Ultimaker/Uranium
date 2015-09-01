// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.1

import UM 1.1 as UM

Dialog
{
    id: base;
    property string object: "";

    property alias newName: nameField.text;

    title: catalog.i18nc("@title:window", "Rename");
    standardButtons: StandardButton.Ok | StandardButton.Cancel;
    modality: Qt.ApplicationModal;

    property variant catalog: UM.I18nCatalog { name: "uranium"; }

    TextField {
        id: nameField;
        width: Screen.devicePixelRatio * 200;
        text: base.object;
    }
}

