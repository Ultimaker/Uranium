// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.0 as UM

Item {
    width: Math.max(14 * UM.Theme.sizes.line.width, childrenRect.width);
    height: Math.max(4.5 * UM.Theme.sizes.line.height, childrenRect.height);

    Button {
        id: resetRotationButton

        //: Reset Rotation tool button
        text: qsTr("Reset")
        iconSource: UM.Theme.icons.rotate_reset;
        //: Reset Rotation tool button tooltip
        tooltip: qsTr("Reset the rotation of the current selection.");

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction("resetRotation");
    }

    CheckBox {
        anchors.left: resetRotationButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.bottom: resetRotationButton.bottom;

        //: Snap Rotation checkbox
        text: qsTr("Snap Rotation");

        style: UM.Theme.styles.checkbox;

        checked: UM.ActiveTool.properties.RotationSnap;
        onClicked: UM.ActiveTool.setProperty("RotationSnap", checked);
    }
}
