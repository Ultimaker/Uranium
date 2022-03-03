// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.1

import UM 1.5 as UM
import Cura 1.5 as Cura

Cura.MessageDialog
{
    property string object: "";

    title: catalog.i18nc("@title:window", "Confirm Remove");
    text: catalog.i18nc("@label (%1 is object name)", "Are you sure you wish to remove %1? This cannot be undone!").arg(object);
    standardButtons: Dialog.Yes | Dialog.No

    property variant catalog: UM.I18nCatalog { name: "uranium"; }
}
