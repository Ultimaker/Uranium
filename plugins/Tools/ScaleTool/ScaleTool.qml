// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    width: Math.max(23 * UM.Theme.sizes.line.width, childrenRect.width);
    height: Math.max(9.5 * UM.Theme.sizes.line.height, childrenRect.height);
    UM.I18nCatalog { id: catalog; name:"uranium"}
    Button
    {
        id: resetScaleButton

        anchors.top: scaleToMaxButton.bottom;
        anchors.topMargin: UM.Theme.sizes.default_margin.height;

        //: Reset scale tool button
        text: catalog.i18nc("@action:button","Reset")
        iconSource: UM.Theme.icons.scale_reset;
        //: Reset scale tool button tooltip
        tooltip: catalog.i18nc("@info:tooltip","Reset the scaling of the current selection.");

        style: UM.Theme.styles.tool_button_panel;

        onClicked: UM.ActiveTool.triggerAction("resetScale");
    }

    Button
    {
        id: scaleToMaxButton

        //: Scale to max tool button
        text: catalog.i18nc("@action:button","Scale to Max");
        iconSource: UM.Theme.icons.scale_max;
        //: Scale to max tool button tooltip
        tooltip: catalog.i18nc("@info:tooltip","Scale to maximum size");

        anchors.top: parent.top;

        style: UM.Theme.styles.tool_button_panel;
        onClicked: UM.ActiveTool.triggerAction("scaleToMax")
    }

    Flow {
        id: checkboxes;

        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.right: parent.right;
        anchors.top: textfields.bottom;
        anchors.topMargin: UM.Theme.sizes.default_margin.height;

        spacing: UM.Theme.sizes.default_margin.height;

        CheckBox
        {
            //: Snap Scaling checkbox
            text: catalog.i18nc("@action:checkbox","Snap Scaling");

            style: UM.Theme.styles.checkbox;

            checked: UM.ActiveTool.properties.ScaleSnap;
            onClicked: UM.ActiveTool.setProperty("ScaleSnap", checked);
        }

        CheckBox
        {
            //: Uniform scaling checkbox
            text: catalog.i18nc("@action:checkbox","Uniform Scaling");

            style: UM.Theme.styles.checkbox;

            checked: !UM.ActiveTool.properties.NonUniformScale;
            onClicked: UM.ActiveTool.setProperty("NonUniformScale", !checked);
        }
    }

    Grid
    {
        id: textfields;

        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.top: parent.top;

        columns: 3;
        flow: Grid.TopToBottom;
        spacing: UM.Theme.sizes.default_margin.width / 2;

        Label
        {
            height: UM.Theme.sizes.setting_control.height;
            text: "X";
            font: UM.Theme.fonts.default;
            color: UM.Theme.colors.text;
            verticalAlignment: Text.AlignVCenter;
        }

        Label
        {
            height: UM.Theme.sizes.setting_control.height;
            text: "Y";
            font: UM.Theme.fonts.default;
            color: UM.Theme.colors.text;
            verticalAlignment: Text.AlignVCenter;
        }

        Label
        {
            height: UM.Theme.sizes.setting_control.height;
            text: "Z";
            font: UM.Theme.fonts.default;
            color: UM.Theme.colors.text;
            verticalAlignment: Text.AlignVCenter;
        }

        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ObjectWidth
            onEditingFinished: UM.ActiveTool.setProperty("ObjectWidth", text);
        }
        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ObjectDepth
            onEditingFinished: UM.ActiveTool.setProperty("ObjectDepth", text);
        }
        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ObjectHeight
            onEditingFinished: UM.ActiveTool.setProperty("ObjectHeight", text);
        }

        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ScaleX * 100;
            onEditingFinished: UM.ActiveTool.setProperty("ScaleX", parseFloat(text) / 100);
        }
        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ScaleZ * 100;
            onEditingFinished: UM.ActiveTool.setProperty("ScaleZ", parseFloat(text) / 100);
        }
        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ScaleY * 100;
            onEditingFinished: UM.ActiveTool.setProperty("ScaleY", parseFloat(text) / 100);
        }
    }
}

