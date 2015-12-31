// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    id: base
    width: Math.max(23 * UM.Theme.sizes.line.width, childrenRect.width);
    height: Math.max(9.5 * UM.Theme.sizes.line.height, childrenRect.height);
    UM.I18nCatalog { id: catalog; name:"uranium"}

    function getPercentage(scale){
        if (snapScalingCheckbox.checked){
            return Math.round(scale * 10) * 10 //rounds the percentage at tens
        }
        else{
            return scale * 100;
        }
    }

    Button
    {
        id: resetScaleButton

        anchors.top: scaleToMaxButton.bottom;
        anchors.topMargin: UM.Theme.sizes.default_margin.height;
        z: 1

        //: Reset scale tool button
        text: catalog.i18nc("@action:button","Reset")
        iconSource: UM.Theme.icons.scale_reset;

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction("resetScale");
    }

    Button
    {
        id: scaleToMaxButton

        //: Scale to max tool button
        text: catalog.i18nc("@action:button","Scale to Max");
        iconSource: UM.Theme.icons.scale_max;

        anchors.top: parent.top;
        z: 1

        style: UM.Theme.styles.tool_button;
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
            id: snapScalingCheckbox
            //: Snap Scaling checkbox
            text: catalog.i18nc("@option:check","Snap Scaling");

            style: UM.Theme.styles.checkbox;

            checked: UM.ActiveTool.properties.ScaleSnap;
            onClicked: {
                UM.ActiveTool.setProperty("ScaleSnap", checked);
                if (snapScalingCheckbox.checked){
                    UM.ActiveTool.setProperty("ScaleX", parseFloat(xPercentage.text) / 100);
                    UM.ActiveTool.setProperty("ScaleY", parseFloat(yPercentage.text) / 100);
                    UM.ActiveTool.setProperty("ScaleZ", parseFloat(zPercentage.text) / 100);
                }
            }
        }

        CheckBox
        {
            //: Uniform scaling checkbox
            text: catalog.i18nc("@option:check","Uniform Scaling");

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
            validator: DoubleValidator
            {
                bottom: 0.1
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("ObjectWidth", text);
        }
        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ObjectDepth
            validator: DoubleValidator
            {
                bottom: 0.1
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("ObjectDepth", text);
        }
        TextField
        {
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.ObjectHeight
            validator: DoubleValidator
            {
                bottom: 0.1
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("ObjectHeight", text);
        }

        TextField
        {
            id: xPercentage
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: base.getPercentage(UM.ActiveTool.properties.ScaleX)
            validator: DoubleValidator
            {
                bottom: 100 * (0.1 / (UM.ActiveTool.properties.ObjectWidth / UM.ActiveTool.properties.ScaleX));
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("ScaleX", parseFloat(text) / 100);
        }
        TextField
        {
            id: zPercentage
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: base.getPercentage(UM.ActiveTool.properties.ScaleZ)
            validator: DoubleValidator
            {
                bottom: 100 * (0.1 / (UM.ActiveTool.properties.ObjectDepth / UM.ActiveTool.properties.ScaleZ));
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("ScaleZ", parseFloat(text) / 100);
        }
        TextField
        {
            id: yPercentage
            width: UM.Theme.sizes.setting_control.width;
            height: UM.Theme.sizes.setting_control.height;
            property string unit: "%";
            style: UM.Theme.styles.text_field;
            text: base.getPercentage(UM.ActiveTool.properties.ScaleY)
            validator: DoubleValidator
            {
                bottom: 100 * (0.1 / (UM.ActiveTool.properties.ObjectHeight / UM.ActiveTool.properties.ScaleY))
                locale: "en_US"
            }

            onEditingFinished: UM.ActiveTool.setProperty("ScaleY", parseFloat(text) / 100);
        }
    }
}
