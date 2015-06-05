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

        checked: UM.ActiveTool.properties.ScaleSnap;
        onClicked: UM.ActiveTool.setProperty("ScaleSnap", checked);
    }

    CheckBox {
        anchors.left: snapCheckbox.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.bottom: parent.bottom;

        //: Uniform scaling checkbox
        text: qsTr("Uniform Scaling");

        style: UM.Theme.styles.checkbox;

        checked: !UM.ActiveTool.properties.NonUniformScale;
        onClicked: UM.ActiveTool.setProperty("NonUniformScale", !checked);
    }

    Grid {
        anchors.bottom: snapCheckbox.top;
        anchors.bottomMargin: UM.Theme.sizes.default_margin.height;
        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;

        columns: 3;
        flow: Grid.TopToBottom;
        spacing: UM.Theme.sizes.default_margin.width / 2;

        Label {
            height: UM.Theme.sizes.setting_control.height;
            text: "X";
            font: UM.Theme.fonts.default;
            verticalAlignment: Text.AlignVCenter;
        }

        Label {
            height: UM.Theme.sizes.setting_control.height;
            text: "Y";
            font: UM.Theme.fonts.default;
            verticalAlignment: Text.AlignVCenter;
        }

        Label {
            height: UM.Theme.sizes.setting_control.height;
            text: "Z";
            font: UM.Theme.fonts.default;
            verticalAlignment: Text.AlignVCenter;
        }

        TextField {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: Math.round(UM.ActiveTool.properties.ObjectWidth)
            onEditingFinished: UM.ActiveTool.setProperty("ObjectWidth", text);
        }
        TextField {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: Math.round(UM.ActiveTool.properties.ObjectDepth)
            onEditingFinished: UM.ActiveTool.setProperty("ObjectDepth", text);
        }
        TextField {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: Math.round(UM.ActiveTool.properties.ObjectHeight)
            onEditingFinished: UM.ActiveTool.setProperty("ObjectHeight", text);
        }

        TextField {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: Math.round(UM.ActiveTool.properties.ScaleX * 100);
            onEditingFinished: UM.ActiveTool.setProperty("ScaleX", parseInt(text) / 100);
        }
        TextField {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: Math.round(UM.ActiveTool.properties.ScaleZ * 100);
            onEditingFinished: UM.ActiveTool.setProperty("ScaleZ", parseInt(text) / 100);
        }
        TextField {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: Math.round(UM.ActiveTool.properties.ScaleY * 100);
            onEditingFinished: UM.ActiveTool.setProperty("ScaleY", parseInt(text) / 100);
        }
    }
}

