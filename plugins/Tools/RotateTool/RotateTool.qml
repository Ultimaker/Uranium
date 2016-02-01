// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    width: Math.max(14 * UM.Theme.sizes.line.width, childrenRect.width);
    height: Math.max(4.5 * UM.Theme.sizes.line.height, childrenRect.height);
    UM.I18nCatalog { id: catalog; name:"uranium"}
    Button
    {
        id: resetRotationButton

        anchors.left: parent.left;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;

        //: Reset Rotation tool button
        text: catalog.i18nc("@action:button","Reset")
        iconSource: UM.Theme.icons.rotate_reset;

        style: UM.Theme.styles.tool_button;
        z: 1

        onClicked: UM.ActiveTool.triggerAction("resetRotation");
    }

    Button
    {
        id: layFlatButton

        anchors.left: resetRotationButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;

        //: Lay Flat tool button
        text: catalog.i18nc("@action:button","Lay flat")
        iconSource: UM.Theme.icons.rotate_layflat;

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction("layFlat");
    }

    CheckBox
    {
        anchors.left: parent.left;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.top: resetRotationButton.bottom;
        anchors.topMargin: UM.Theme.sizes.default_margin.width;

        //: Snap Rotation checkbox
        text: catalog.i18nc("@action:checkbox","Snap Rotation");

        style: UM.Theme.styles.checkbox;

        checked: UM.ActiveTool.properties.getValue("RotationSnap");
        onClicked: UM.ActiveTool.setProperty("RotationSnap", checked);
    }
}
