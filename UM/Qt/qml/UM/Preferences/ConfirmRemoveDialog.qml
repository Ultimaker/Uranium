// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1

import UM 1.1 as UM

MessageDialog
{
    property string object: "";

    icon: StandardIcon.Question;
    title: catalog.i18nc("@title:window", "Confirm Remove");
    text: catalog.i18nc("@label (%1 is object name)", "Are you sure you wish to remove %1? This cannot be undone!").arg(object);
    standardButtons: StandardButton.Yes | StandardButton.No;
    modality: Qt.ApplicationModal;

    property variant catalog: UM.I18nCatalog { name: "uranium"; }
}
