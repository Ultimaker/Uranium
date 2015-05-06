// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.0 as UM

Item {
    Button {
        id: resetScaleButton

        anchors.bottom: parent.bottom;

        //: Reset scale tool button
        text: qsTr("Reset")
        iconSource: UM.Theme.icons.scale_reset;
        //: Reset scale tool button tooltip
        tooltip: qsTr("Reset the scaling of the current selection.");

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction("resetScale");
    }

    Button {
        id: scaleToMaxButotn

        //: Scale to max tool button
        text: qsTr("Scale to Max");
        iconSource: UM.Theme.icons.scale_max;
        //: Scale to max tool button tooltip
        tooltip: qsTr("Scale to maximum size");

        anchors.bottom: resetScaleButton.top;
        anchors.bottomMargin: UM.Theme.sizes.default_margin.height;

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction("scaleToMax")
    }

    CheckBox {
        id: snapCheckbox;

        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.bottom: parent.bottom;

        //: Snap Scaling checkbox
        text: qsTr("Snap Scaling");

        style: UM.Theme.styles.checkbox;

        checked: UM.ActiveTool.getProperty("ScaleSnap");
        onClicked: UM.ActiveTool.setProperty("ScaleSnap", checked);
    }

    CheckBox {
        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.top: resetScaleButton.top;

        //: Uniform scaling checkbox
        text: qsTr("Uniform Scaling");

        style: UM.Theme.styles.checkbox;

        checked: !UM.ActiveTool.getProperty("NonUniformScale");
        onClicked: UM.ActiveTool.setProperty("NonUniformScale", !checked);
    }
}

